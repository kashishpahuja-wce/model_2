import cv2
import numpy as np
from scipy.spatial.distance import cosine
import os
import math

from app import add_noise, add_watermark, compress_image

def cosine_similarity(img1, img2):
    return 1 - cosine(img1.flatten().astype(np.float64), img2.flatten().astype(np.float64))

def calculate_psnr(img1, img2):
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0) - 10 * math.log10(mse)

def main():
    orig_path = "static/output/original.png"
    if not os.path.exists(orig_path):
        print("Original image not found in static/output.")
        return
        
    orig_img = cv2.imread(orig_path)
    if orig_img is None:
        print("Failed to read image.")
        return

    psnr_vals = []
    cos_vals = []
    
    print("Running pipeline 20 times to find min/max values...")
    for i in range(20):
        noisy = add_noise(orig_img.copy())
        watermarked = add_watermark(noisy)
        compressed = compress_image(watermarked)
        
        p = calculate_psnr(orig_img, compressed)
        c = cosine_similarity(orig_img, compressed)
        
        psnr_vals.append(p)
        cos_vals.append(c)
        
    print(f"PSNR (Quality) - Min: {min(psnr_vals):.2f} dB, Max: {max(psnr_vals):.2f} dB")
    print(f"Cosine Similarity - Min: {min(cos_vals):.5f}, Max: {max(cos_vals):.5f}")

if __name__ == "__main__":
    main()
