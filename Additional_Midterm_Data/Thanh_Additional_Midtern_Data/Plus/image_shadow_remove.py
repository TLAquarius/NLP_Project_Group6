import cv2
import numpy as np
from PIL import Image
import os

def process_book_image(input_path, output_path):
    '''
    Extract from the PDF and split roughly the Quoc Ngu pages images

    Parameters
    ----------
        input_path: str
            The image path
        output_path: str
            The output path
    Returns
    -------
    '''
    # Load image using Pillow (PIL)
    try:
        img_pil = Image.open(input_path)
        img_pil = img_pil.convert("RGB")  # Convert to standard RGB format
        img = np.array(img_pil)  # Convert PIL image to NumPy array (for OpenCV)
    except Exception as e:
        print(f"Error loading image with Pillow: {e}")
        return

    # Process the image using OpenCV
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Perform Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to remove shadows
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 21, 10)

    # Invert the image to make text white and background black
    inverted = cv2.bitwise_not(binary)

    # Use morphological operations to remove small noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)

    # Optional: Increase thickness of the text for clarity
    thickened = cv2.dilate(cleaned, kernel, iterations=1)

    # Invert back for printing (black text on white background)
    result = cv2.bitwise_not(thickened)

    # Convert the result back to a PIL image
    result_pil = Image.fromarray(result)

    # Save the processed image using PIL (no quality loss with PNG)
    result_pil.save(output_path, format='PNG')  # You can also change the format to JPEG if needed
    print(f"Processed image saved at: {output_path}")

def main():
    # Replace with your input image path to the extracted Quoc Ngu images
    image_folder = "Quoc-Ngu_image"

    # Replace with your desired output path
    output_folder = f"{image_folder}_preprocess"
    os.makedirs(output_folder, exist_ok=True)

    pdf_name = "Sách Nôm công giáo 1995 - 100 - Tu Chung Luoc Thuyet"
    start_page = int(input("Enter the starting page to process: "))
    end_page = int(input("Enter the ending page to process: "))

    # Process the image
    for i in range(start_page, end_page + 1):
        image_file_path = f"{image_folder}\\{pdf_name}_page{i:03}.png"
        output_path = f"{output_folder}\\{pdf_name}_page{i:03}.png"
        if (not os.path.exists(image_file_path)):
            print(f"[+] {image_file_path} not existed")
            continue
        process_book_image(image_file_path, output_path)

if __name__ == "__main__":
    main()
