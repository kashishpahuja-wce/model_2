from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
from PIL import Image
from scipy.fft import dct, idct
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================================================
# FACE DETECTION — used only for the light warp pass
# ===============================================================

def find_face_mask(image):
    """Detect faces and return a soft mask covering the face area."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    mask = np.zeros(gray.shape, dtype=np.uint8)
    if len(faces) == 0:
        return mask

    for (x, y, w, h) in faces:
        # Expand the face box slightly
        pad_x = int(w * 0.1)
        pad_y = int(h * 0.1)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(image.shape[1], x + w + pad_x)
        y2 = min(image.shape[0], y + h + pad_y)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

    # Soft-edge the mask so there's no hard boundary
    k = 31
    mask = cv2.GaussianBlur(mask, (k, k), 0)
    return mask


# ===============================================================
# ATTACK A: Chroma jitter (YCbCr) — invisible, disrupts color embeddings
# ===============================================================

def _attack_chroma_jitter(image):
    """Shift Cb/Cr channels smoothly across the whole image.
    Humans are ~4x less sensitive to chroma than luminance so this
    is essentially invisible, but AI colour-space embeddings break."""
    ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb).astype(np.int16)
    h, w  = image.shape[:2]

    epsilon  = np.random.uniform(8.0, 18.0)          # strong but in chroma space
    grid_div = np.random.randint(10, 30)              # coarseness of the blob field
    blur_k   = np.random.choice([19, 25, 31, 37])    # smooth it heavily

    for ch in [1, 2]:   # Cb and Cr only — leave Y (luminance) untouched
        raw  = np.random.normal(0, 1, (h // grid_div + 1, w // grid_div + 1)).astype(np.float32)
        up   = cv2.resize(raw, (w, h), interpolation=cv2.INTER_CUBIC)
        up   = cv2.GaussianBlur(up, (blur_k, blur_k), 0)
        m    = np.max(np.abs(up)) + 1e-6
        ycbcr[:, :, ch] += (up / m * epsilon).astype(np.int16)

    np.clip(ycbcr, 0, 255, out=ycbcr)
    return cv2.cvtColor(ycbcr.astype(np.uint8), cv2.COLOR_YCrCb2BGR)


# ===============================================================
# ATTACK B: High-frequency sinusoidal noise — disrupts CNN spatial features
# ===============================================================

def _attack_sinusoid(image):
    """Inject rotated sinusoidal waves at frequencies where CNNs are
    most sensitive. Delta is tiny per-pixel but accumulates across
    the whole image, making feature map activations inconsistent."""
    h, w = image.shape[:2]
    out  = image.astype(np.float64)

    epsilon   = np.random.uniform(3.0, 8.0)
    num_waves = np.random.randint(3, 7)

    for _ in range(num_waves):
        freq    = np.random.uniform(0.05, 0.50)      # random spatial frequency
        phase_x = np.random.uniform(0, 2 * np.pi)
        phase_y = np.random.uniform(0, 2 * np.pi)
        angle   = np.random.uniform(0, np.pi)        # random orientation

        xs = np.arange(w, dtype=np.float64)
        ys = np.arange(h, dtype=np.float64)
        xx, yy = np.meshgrid(xs, ys)

        rx = xx * np.cos(angle) + yy * np.sin(angle)
        ry = -xx * np.sin(angle) + yy * np.cos(angle)

        wave = np.sin(2 * np.pi * freq * rx + phase_x) * \
               np.cos(2 * np.pi * freq * ry + phase_y)

        for c in range(3):
            strength = np.random.uniform(epsilon * 0.3, epsilon)
            out[:, :, c] += wave * strength

    return np.clip(out, 0, 255).astype(np.uint8)


# ===============================================================
# ATTACK C: Laplacian pyramid — attacks every scale simultaneously
# ===============================================================

def _attack_laplacian_pyramid(image):
    """Decompose the image into frequency bands (pyramid), inject noise
    into each band independently, then reconstruct. Confuses both
    low-level (edge/texture) and high-level (semantic) CNN layers."""
    epsilon = np.random.uniform(6.0, 14.0)
    levels  = np.random.randint(3, 6)

    # Build Gaussian pyramid
    gp = [image.astype(np.float64)]
    for _ in range(levels):
        gp.append(cv2.pyrDown(gp[-1].astype(np.float32)).astype(np.float64))

    # Build Laplacian pyramid
    lp = []
    for i in range(levels):
        size = (gp[i].shape[1], gp[i].shape[0])
        up   = cv2.pyrUp(gp[i + 1].astype(np.float32), dstsize=size).astype(np.float64)
        lp.append(gp[i] - up)

    # Inject noise into each level with random per-level strength
    for i in range(len(lp)):
        strength = epsilon * np.random.uniform(0.3, 1.0)
        nh, nw   = lp[i].shape[:2]
        lp[i]   += np.random.normal(0, strength, (nh, nw, 3))

    # Reconstruct
    recon = gp[levels].astype(np.float64)
    for i in range(levels - 1, -1, -1):
        size  = (lp[i].shape[1], lp[i].shape[0])
        recon = cv2.pyrUp(recon.astype(np.float32), dstsize=size).astype(np.float64)
        recon = recon + lp[i]

    return np.clip(recon, 0, 255).astype(np.uint8)


# ===============================================================
# ATTACK D: DCT coefficient perturbation — targets texture features
# ===============================================================

def _attack_dct_global(image):
    """Perturb mid/high DCT coefficients across the whole image in 8×8 blocks.
    Works exactly like JPEG artifacts but targeted at the frequencies CNNs use
    for face texture, not the ones humans notice."""
    out   = image.copy()
    h, w  = image.shape[:2]
    block = 8
    # Randomly skip ~60% of blocks so the effect is spread, not uniform
    skip_prob = np.random.uniform(0.5, 0.7)

    for c in range(3):
        channel = out[:, :, c].astype(np.float64)
        for by in range(0, h - block + 1, block):
            for bx in range(0, w - block + 1, block):
                if np.random.random() < skip_prob:
                    continue
                patch  = channel[by:by + block, bx:bx + block]
                coeffs = dct(dct(patch, axis=0, norm='ortho'), axis=1, norm='ortho')

                strength = np.random.uniform(8.0, 20.0)
                noise    = np.random.normal(0, strength, (block, block))
                # Protect the DC term and the 2 lowest-freq coefficients
                noise[0, 0] = 0
                noise[0, 1] *= 0.1
                noise[1, 0] *= 0.1

                coeffs += noise
                channel[by:by + block, bx:bx + block] = \
                    idct(idct(coeffs, axis=0, norm='ortho'), axis=1, norm='ortho')

        out[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)

    return out


# ===============================================================
# ATTACK E: Gentle face warp — breaks landmark geometry, invisible
# ===============================================================

def _attack_face_warp(image, mask):
    """Very gentle elastic warp applied only inside the face mask.
    Strength is low (2–5 px) so it looks completely natural to humans
    but breaks the precise landmark distances face-recognition uses."""
    if mask.sum() == 0:
        return image

    h, w    = image.shape[:2]
    strength = np.random.uniform(2.0, 5.0)     # very subtle
    smooth   = np.random.choice([51, 61, 71])  # very smooth so no visible warp

    dx = cv2.GaussianBlur(
        (np.random.rand(h, w).astype(np.float32) - 0.5) * 2 * strength,
        (smooth, smooth), 0
    )
    dy = cv2.GaussianBlur(
        (np.random.rand(h, w).astype(np.float32) - 0.5) * 2 * strength,
        (smooth, smooth), 0
    )

    mf = (mask / 255.0).astype(np.float32)
    dx *= mf
    dy *= mf

    map_x, map_y = np.meshgrid(np.arange(w, dtype=np.float32),
                                np.arange(h, dtype=np.float32))
    map_x += dx
    map_y += dy

    warped = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REFLECT)

    out   = image.copy()
    mask3 = cv2.merge([mask, mask, mask])
    out[mask3 > 0] = warped[mask3 > 0]
    return out


# ===============================================================
# MAIN PIPELINE — randomly selects a combination each run
# ===============================================================

# All available global attacks
_GLOBAL_ATTACKS = [
    _attack_chroma_jitter,
    _attack_sinusoid,
    _attack_laplacian_pyramid,
    _attack_dct_global,
]

def protect_image(image):
    """Choose a random subset of attacks each run so the protection
    pattern is unpredictable and no single technique is over-applied.
    The image should look completely natural to humans."""

    # --- Face warp (gentle, only if face is detected) ---
    mask    = find_face_mask(image)
    result  = _attack_face_warp(image, mask)

    # --- Randomly pick 2 or 3 of the 4 global attacks ---
    num_attacks = np.random.randint(2, 4)
    chosen      = np.random.choice(len(_GLOBAL_ATTACKS), size=num_attacks, replace=False)

    for idx in chosen:
        result = _GLOBAL_ATTACKS[idx](result)

    return result


# ===============================================================
# FLASK ROUTES
# ===============================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    output_urls = {}

    if request.method == 'POST':
        img_file = request.files.get('image')
        if not img_file:
            return redirect(request.url)

        # Save original
        orig_path = os.path.join(UPLOAD_FOLDER, 'original.png')
        img = Image.open(img_file.stream).convert('RGB')
        img.save(orig_path)

        img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Apply protection
        protected = protect_image(img_arr)

        out_path = os.path.join(UPLOAD_FOLDER, 'processed.png')
        cv2.imwrite(out_path, protected)

        output_urls = {
            'original':  f"/{orig_path.replace('\\', '/')}",
            'processed': f"/{out_path.replace('\\', '/')}",
        }

    return render_template('index.html', output=output_urls)


if __name__ == '__main__':
    app.run(debug=True)
