import cv2
import numpy as np
import os
from app import add_noise, find_face_regions

def test_pipeline():
    # Attempt to load a sample image. We'll use a blank image with a face-like structure if none exists,
    # or just look for any image in static/output or the current directory.
    # Let's generate a quick dummy image or use an existing one if the user has one.
    # For now, we will just print that we need an image to test.
    
    test_img_path = 'test_image.jpg'
    
    # If test_image.jpg doesn't exist, we will create a dummy colorful image
    # though mediapipe needs a real human face to work.
    if not os.path.exists(test_img_path):
        print("Please provide a real human face image named 'test_image.jpg' in the project root to run this test properly.")
        return

    img = cv2.imread(test_img_path)
    if img is None:
        print("Failed to read image.")
        return

    print("Running face region detection...")
    mask = find_face_regions(img)
    cv2.imwrite('test_mask.png', mask)
    print(f"Mask sum: {mask.sum()}, saved to test_mask.png")

    print("Running full pipeline...")
    out_img = add_noise(img)
    cv2.imwrite('test_output.png', out_img)
    print("Output saved to test_output.png")

if __name__ == '__main__':
    test_pipeline()
