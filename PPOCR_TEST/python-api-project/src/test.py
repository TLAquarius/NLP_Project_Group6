# FILE: /python-api-project/python-api-project/src/test.py
from paddleocr import PaddleOCR, draw_ocr
import os
import cv2

# Initialize PaddleOCR
ocr = PaddleOCR(
    det_model_dir='D:/PPOCR_TEST/det/final_det_inference',  # Model detection
    rec_model_dir='D:/PPOCR_TEST/rec/ch_PP-OCRv3_rec_infer',  # Model recognition
    use_gpu=False  # Set to True if using GPU
)

def process_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found or unable to load: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform OCR on the image
    results = ocr.ocr(image)

    # Extract detected text
    detected_text = [line[1][0] for line in results[0]]

    return detected_text

# Additional utility functions can be added here if needed