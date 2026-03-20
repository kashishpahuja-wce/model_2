from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
import base64
import requests
import uuid
from dotenv import load_dotenv

# Load environment variables for local dev
load_dotenv()

app = Flask(__name__)
# Enable CORS for local dev
CORS(app)

BLOB_READ_WRITE_TOKEN = os.environ.get('BLOB_READ_WRITE_TOKEN')

def upload_to_blob(image_bytes, filename):
    """Upload bytes to Vercel Blob and return the URL."""
    if not BLOB_READ_WRITE_TOKEN:
        print("Warning: BLOB_READ_WRITE_TOKEN not set. Falling back to base64.")
        return None

    # Vercel Blob PUT implementation via HTTP API
    url = f"https://blob.vercel-storage.com/{filename}"
    headers = {
        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": "2022-09-01"
    }
    
    try:
        response = requests.put(url, data=image_bytes, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('url')
        else:
            print(f"Blob Upload Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Blob Upload Exception: {str(e)}")
        return None

def find_face_mask(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    mask = np.zeros(gray.shape, dtype=np.uint8)
    if len(faces) == 0:
        return mask

    for (x, y, w, h) in faces:
        pad_x = int(w * 0.1)
        pad_y = int(h * 0.1)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(image.shape[1], x + w + pad_x)
        y2 = min(image.shape[0], y + h + pad_y)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

    k = 31
    mask = cv2.GaussianBlur(mask, (k, k), 0)
    return mask

def _attack_chroma_jitter(image):
    ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb).astype(np.int16)
    h, w  = image.shape[:2]
    epsilon  = np.random.uniform(8.0, 18.0)
    grid_div = np.random.randint(10, 30)
    blur_k   = np.random.choice([19, 25, 31, 37])
    for ch in [1, 2]:
        raw  = np.random.normal(0, 1, (h // grid_div + 1, w // grid_div + 1)).astype(np.float32)
        up   = cv2.resize(raw, (w, h), interpolation=cv2.INTER_CUBIC)
        up   = cv2.GaussianBlur(up, (blur_k, blur_k), 0)
        m    = np.max(np.abs(up)) + 1e-6
        ycbcr[:, :, ch] += (up / m * epsilon).astype(np.int16)

    np.clip(ycbcr, 0, 255, out=ycbcr)
    return cv2.cvtColor(ycbcr.astype(np.uint8), cv2.COLOR_YCrCb2BGR)

def _attack_sinusoid(image):
    h, w = image.shape[:2]
    out  = image.astype(np.float64)
    epsilon   = np.random.uniform(3.0, 8.0)
    num_waves = np.random.randint(3, 7)
    for _ in range(num_waves):
        freq    = np.random.uniform(0.05, 0.50)
        phase_x = np.random.uniform(0, 2 * np.pi)
        phase_y = np.random.uniform(0, 2 * np.pi)
        angle   = np.random.uniform(0, np.pi)
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

def _attack_laplacian_pyramid(image):
    epsilon = np.random.uniform(6.0, 14.0)
    levels  = np.random.randint(3, 6)
    gp = [image.astype(np.float64)]
    for _ in range(levels):
        gp.append(cv2.pyrDown(gp[-1].astype(np.float32)).astype(np.float64))
    lp = []
    for i in range(levels):
        size = (gp[i].shape[1], gp[i].shape[0])
        up   = cv2.pyrUp(gp[i + 1].astype(np.float32), dstsize=size).astype(np.float64)
        lp.append(gp[i] - up)
    for i in range(len(lp)):
        strength = epsilon * np.random.uniform(0.3, 1.0)
        nh, nw   = lp[i].shape[:2]
        lp[i]   += np.random.normal(0, strength, (nh, nw, 3))
    recon = gp[levels].astype(np.float64)
    for i in range(levels - 1, -1, -1):
        size  = (lp[i].shape[1], lp[i].shape[0])
        recon = cv2.pyrUp(recon.astype(np.float32), dstsize=size).astype(np.float64)
        recon = recon + lp[i]
    return np.clip(recon, 0, 255).astype(np.uint8)

def _attack_dct_global(image):
    out   = image.copy()
    h, w  = image.shape[:2]
    block = 8
    skip_prob = np.random.uniform(0.5, 0.7)
    for c in range(3):
        channel = out[:, :, c].astype(np.float64)
        for by in range(0, h - block + 1, block):
            for bx in range(0, w - block + 1, block):
                if np.random.random() < skip_prob:
                    continue
                patch  = channel[by:by + block, bx:bx + block].astype(np.float32)
                coeffs = cv2.dct(patch)
                strength = np.random.uniform(8.0, 20.0)
                noise    = np.random.normal(0, strength, (block, block)).astype(np.float32)
                noise[0, 0] = 0
                noise[0, 1] *= 0.1
                noise[1, 0] *= 0.1
                coeffs += noise
                channel[by:by + block, bx:bx + block] = cv2.idct(coeffs)
        out[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)
    return out

def _attack_face_warp(image, mask):
    if mask.sum() == 0:
        return image
    h, w    = image.shape[:2]
    strength = np.random.uniform(2.0, 5.0)
    smooth   = np.random.choice([51, 61, 71])
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

_GLOBAL_ATTACKS = [
    _attack_chroma_jitter,
    _attack_sinusoid,
    _attack_laplacian_pyramid,
    _attack_dct_global,
]

def protect_image(image):
    mask    = find_face_mask(image)
    result  = _attack_face_warp(image, mask)
    num_attacks = np.random.randint(2, 4)
    chosen      = np.random.choice(len(_GLOBAL_ATTACKS), size=num_attacks, replace=False)
    for idx in chosen:
        result = _GLOBAL_ATTACKS[idx](result)
    return result

@app.route('/api/process', methods=['POST', 'OPTIONS'])
def process():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    img_file = request.files['image']
    file_bytes = np.frombuffer(img_file.read(), np.uint8)
    img_arr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img_arr is None:
        return jsonify({'error': 'Invalid image file'}), 400

    # Apply protection
    protected = protect_image(img_arr)

    # Encode images to bytes
    _, orig_buffer = cv2.imencode('.png', img_arr)
    _, prot_buffer = cv2.imencode('.png', protected)
    
    # Generate unique filenames
    uid = uuid.uuid4().hex[:8]
    orig_filename = f"original_{uid}.png"
    prot_filename = f"protected_{uid}.png"

    # Upload to Vercel Blob
    orig_url = upload_to_blob(orig_buffer.tobytes(), orig_filename)
    prot_url = upload_to_blob(prot_buffer.tobytes(), prot_filename)

    # Fallback to base64 if upload failed or token is missing
    if not prot_url:
        encoded_string = base64.b64encode(prot_buffer).decode('utf-8')
        prot_url = f"data:image/png;base64,{encoded_string}"
    
    if not orig_url:
        encoded_orig = base64.b64encode(orig_buffer).decode('utf-8')
        orig_url = f"data:image/png;base64,{encoded_orig}"

    return jsonify({
        'processed': prot_url,
        'original': orig_url
    })

# Keep this for local dev via `python index.py`
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
