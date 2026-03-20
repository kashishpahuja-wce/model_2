from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------
# FACE REGION-FOCUSED NOISE (eyes + jaw)
# -------------------------------

def _apply_noise_mask(base_img, mask, sigma=10):
    """Apply Gaussian noise only where mask is nonzero."""
    noise = np.random.normal(0, sigma, base_img.shape).astype(np.int16)
    out = base_img.astype(np.int16)
    out[mask > 0] += noise[mask > 0]
    np.clip(out, 0, 255, out=out)
    return out.astype(np.uint8)


def find_face_regions(image):
    """Return a mask that covers the eyes and jaw region based on eye detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eyes_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    eyes = eyes_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=10, minSize=(20, 20)
    )

    mask = np.zeros(gray.shape, dtype=np.uint8)

    if len(eyes) < 2:
        # If we cannot reliably detect both eyes, don't apply any protection.
        return mask

    # Choose two largest eyes (likely left+right)
    eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]

    # Compute estimated face center and size from eye positions
    centers = [(x + w // 2, y + h // 2) for (x, y, w, h) in eyes]
    eye_center = (int((centers[0][0] + centers[1][0]) / 2), int((centers[0][1] + centers[1][1]) / 2))
    eye_dist = abs(centers[0][0] - centers[1][0])

    # Eye mask: slightly enlarged around the detected eyes
    for (x, y, w, h) in eyes:
        pad = int(max(w, h) * 0.6)
        cv2.rectangle(mask, (x - pad, y - pad), (x + w + pad, y + h + pad), 255, -1)

    # Jaw mask: below eye line, roughly same width as distance between eyes
    # Randomize multipliers slightly to add variance
    w_mult = np.random.uniform(2.3, 2.7)
    h_mult = np.random.uniform(0.6, 0.7)
    top_mult = np.random.uniform(0.15, 0.25)
    
    face_width = int(eye_dist * w_mult)
    face_height = int(face_width * h_mult)
    jaw_top = eye_center[1] + int(face_height * top_mult)
    jaw_bottom = jaw_top + face_height
    jaw_left = int(eye_center[0] - face_width / 2)
    jaw_right = int(eye_center[0] + face_width / 2)

    jaw_top = max(jaw_top, 0)
    jaw_bottom = min(jaw_bottom, gray.shape[0])
    jaw_left = max(jaw_left, 0)
    jaw_right = min(jaw_right, gray.shape[1])

    cv2.rectangle(mask, (jaw_left, jaw_top), (jaw_right, jaw_bottom), 255, -1)

    # Make mask slightly smoother (soft edges) so changes blend better
    # Randomize the kernel size to vary the softness
    blur_k = np.random.choice([15, 17, 19, 21, 23, 25])
    mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)
    _, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)

    return mask


def _pixelate_region(image, mask, pixel_size=14):
    """Pixelate only the masked region to preserve overall image quality."""
    h, w = image.shape[:2]
    small = cv2.resize(image, (max(1, w // pixel_size), max(1, h // pixel_size)), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    out = image.copy()
    mask3 = cv2.merge([mask, mask, mask])
    out[mask3 > 0] = pixelated[mask3 > 0]
    return out


def add_noise(image):
    mask = find_face_regions(image)
    if mask.sum() == 0:
        return image

    # Start by pixelating the masked regions (eye + jaw)
    # Randomize pixelation block size
    psize = np.random.randint(12, 25)
    protected = _pixelate_region(image, mask, pixel_size=psize)

    # Add subtle noise only in masked regions (hard for humans to see but detectable by AI)
    sigma = np.random.uniform(2.0, 8.0)
    noise = np.random.normal(0, sigma, image.shape).astype(np.int16)
    out = protected.astype(np.int16)
    mask3 = cv2.merge([mask, mask, mask])
    out[mask3 > 0] += noise[mask3 > 0]
    np.clip(out, 0, 255, out=out)

    return out.astype(np.uint8)

# -------------------------------
# METHOD 2: Invisible watermark
# -------------------------------
def add_watermark(image):
    watermark = np.zeros_like(image)
    step = np.random.randint(8, 15)
    intensity = np.random.randint(5, 15)
    watermark[::step, ::step] = intensity  # subtle random pattern
    watermarked = cv2.add(image, watermark)
    return watermarked

# -------------------------------
# METHOD 4: Preserve quality (no downscale)
# -------------------------------
def compress_image(image):
    # Keep full resolution and high quality; random JPEG compression quality
    quality = np.random.randint(85, 96)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, encoded = cv2.imencode('.jpg', image, encode_param)
    if success:
        return cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    return image

@app.route('/', methods=['GET', 'POST'])
def index():
    output_urls = {}

    if request.method == 'POST':
        img_file = request.files.get('image')
        if not img_file:
            return redirect(request.url)

        # Save original for preview
        orig_path = os.path.join(UPLOAD_FOLDER, 'original.png')
        img = Image.open(img_file.stream).convert('RGB')
        img.save(orig_path)

        img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Apply protections
        noisy = add_noise(img_arr)
        watermarked = add_watermark(noisy)
        compressed = compress_image(watermarked)

        out_path = os.path.join(UPLOAD_FOLDER, 'processed.png')
        cv2.imwrite(out_path, compressed)

        output_urls = {
            'original': f"/{orig_path.replace('\\', '/')}",
            'processed': f"/{out_path.replace('\\', '/')}",
        }

    return render_template('index.html', output=output_urls)

if __name__ == '__main__':
    app.run(debug=True)
