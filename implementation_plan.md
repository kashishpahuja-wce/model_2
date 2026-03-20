# Precise Eye and Jaw Obfuscation Scheme

The goal is to accurately locate the eyes and jaw of a person in an uploaded picture, apply a minute-region pixel-level blur (average color) specifically to those regions, and then add subtle noise over them to confuse AI models while remaining visually unobtrusive to human viewers.

## Proposed Changes

### Requirements Update
- **[requirements.txt](file:///c:/chatgpt_photogaurd/requirements.txt)**: Add `mediapipe` for high-precision facial landmark detection, as Haar cascades are insufficient for exact jawline and eye contours.

### Core Implementation
- **[app.py](file:///c:/chatgpt_photogaurd/app.py)**:
  - Replace [find_face_regions](file:///c:/chatgpt_photogaurd/app.py#24-72) with a robust Mediapipe Face Mesh based function.
  - Define precise landmark indices for the left eye, right eye, and the jawline/chin area.
  - Create a polygon mask from these landmarks.
  - Use a block mean filter (`cv2.resize` interpolation linear downscale then nearest upscale) to "change the pixcels of eye by bluring the image at pixel level to its color of pixel of that minute region". 
  - Apply Gaussian noise strictly inside the masked regions.

#### [MODIFY] app.py
- Import `mediapipe as mp`.
- Create a `find_face_regions_mp(image)` function replacing Haar cascades to return precise binary masks.
- Update [add_noise(image)](file:///c:/chatgpt_photogaurd/app.py#86-102) to use this precise mask.
- Update [_pixelate_region](file:///c:/chatgpt_photogaurd/app.py#74-84) to ensure it computes the aggregate color of block regions.

#### [MODIFY] requirements.txt
- Append `mediapipe`.

## Verification Plan

### Manual Verification
- Since there are no existing automated tests in this codebase, we will write a temporary scratch script `tmp_test.py` to read an image, apply [add_noise()](file:///c:/chatgpt_photogaurd/app.py#86-102), and save the result.
- We will visually review the output to confirm:
  1. The eyes and jaw are correctly and exactly isolated (not just bounding boxes).
  2. The regions are blurred uniformly into blocks (pixelated).
  3. Subtle noise is visible upon close inspection but otherwise unobtrusive.
