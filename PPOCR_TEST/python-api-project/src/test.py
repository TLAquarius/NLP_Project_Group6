from paddleocr import PaddleOCR, draw_ocr
import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import base64

# Initialize PaddleOCR
ocr = PaddleOCR(
    det_model_dir='..//..//det//final_det_inference',  # Model detection
    rec_model_dir='..//../rec//ch_PP-OCRv3_rec_infer',  # Model recognition
    use_gpu=False  # Set to True if using GPU
)

def sort_box(points):
    points = np.array(points)  # Convert to numpy array
    sorted_indices = np.lexsort((points[:, 0], points[:, 1]))  # Sort by y first, then x
    top_two = points[sorted_indices[:2]]  # Get top 2 points
    bottom_two = points[sorted_indices[2:]]  # Get bottom 2 points

    # Determine top-left and top-right
    top_two = top_two[np.argsort(top_two[:, 0])]  # Sort by x
    top_left, top_right = top_two[0], top_two[1]

    # Determine bottom-left and bottom-right
    bottom_two = bottom_two[np.argsort(bottom_two[:, 0])]  # Sort by x
    bottom_left, bottom_right = bottom_two[0], bottom_two[1]

    # Combine according to the rule
    return [top_left.tolist(), top_right.tolist(), bottom_right.tolist(), bottom_left.tolist()]

def process_image(image):
    # # Load the image
    # image = cv2.imread(image_path)
    # if image is None:
    #     raise ValueError(f"Image not found or unable to load: {image_path}")
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # # Perform OCR on the image
    result = ocr.ocr(np.array(image), det=True, rec=True)

    # Extract coordinates, text, and confidence scores
    boxes = [line[0] for line in result[0]]
    texts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]
    print("Hello world 1 ")

    # Sort the boxes and reorder texts and scores accordingly
    sorted_indices = sorted(range(len(boxes)), key=lambda i: sort_box(boxes[i]))
    boxes = [boxes[i] for i in sorted_indices]
    texts = [texts[i] for i in sorted_indices]
    scores = [scores[i] for i in sorted_indices]
    print("Hello world 2 ")

    # Path to the font file
    font_path = './/NomNaTong-Regular.ttf'

    # Draw bounding box and text on the image
    result_image = draw_ocr(image, boxes, texts, scores, font_path=font_path)

    # Convert the result image to Base64
    buffered = BytesIO()
    Image.fromarray(result_image).save(buffered, format="JPEG")
    result_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Return the result as a dictionary
    return {
        'detected_text': [{'text': text, 'confidence': score} for text, score in zip(texts[::-1], scores[::-1])],
        'image': result_image_base64  # Image returned as Base64
    }