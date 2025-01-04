import cv2
import numpy as np
from PIL import Image
import os

def deskew_image(input_path, output_path):
    '''
    Deskew the image base on the angle of the guessed vertical line

    Parameters
    ----------
        input_path: str
            The image path
        output_path: str
            The output path
    Returns
    -------
    '''
    try:
        # Load the preprocessed image
        img_pil = Image.open(input_path)
        img = np.array(img_pil)  # Convert PIL image to NumPy array (for OpenCV)
    except Exception as e:
        print(f"Error loading image with Pillow: {e}")
        return

    # Check if the image is already in grayscale (1 channel)
    if len(img.shape) == 3:
        # Convert to grayscale for edge detection (only if the image is in RGB/BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        # If the image is already grayscale, use it directly
        gray = img

    # Perform Canny edge detection to find edges in the image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Use Hough Line Transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    # Check if any lines are detected
    if lines is not None:
        # Find the longest vertical line by filtering based on the angle
        longest_vertical_line = None
        max_length = 0

        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # Calculate line length

            # Calculate the angle of the line
            delta_x = x2 - x1
            delta_y = y2 - y1
            angle = np.degrees(np.arctan2(delta_y, delta_x))  # Angle in degrees

            # Check if the line is almost vertical (angle close to 90° or -90°)
            if (angle > 80 and angle < 100) or (angle < -80 and angle > -100):
                # If it's the longest vertical line, keep track of it
                if length > max_length:
                    max_length = length
                    longest_vertical_line = (x1, y1, x2, y2)

        if longest_vertical_line:
            # Calculate the angle of the longest vertical line relative to the horizontal axis
            x1, y1, x2, y2 = longest_vertical_line
            delta_x = x2 - x1
            delta_y = y2 - y1
            angle = np.degrees(np.arctan2(delta_y, delta_x))  # Angle in degrees

            # Since we want to rotate the image so that the line becomes vertical (0 degrees), calculate the rotation angle
            if angle > 0:  # If the line is leaning right (positive angle)
                rotation_angle = angle - 90
            else:  # If the line is leaning left (negative angle)
                rotation_angle = angle + 90

            # Get image dimensions and rotate the image
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
            rotated_image = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                                           borderValue=(255, 255, 255))

            # Convert the final deskewed image back to a PIL image
            result_pil = Image.fromarray(rotated_image)

            # Save the deskewed image
            result_pil.save(output_path, format='PNG')  # Change to 'JPEG' if needed
            print(f"Deskewed image saved at: {output_path}")
        else:
            print("No valid vertical lines detected for deskewing.")
    else:
        print("No lines detected in the image.")

def main():
    # Path to the folder contain cropped images
    image_folder = "Han-Nom_image_khanh_preprocess_temp"

    # Path to the output folder
    output_folder = "Han-Nom_image_khanh_preprocess"
    os.makedirs(output_folder, exist_ok=True)

    # PDF file name
    pdf_name = "Sách Nôm công giáo 1995 - 110 - Tu Nguyen Yeu Ly - Phan II"
    start_page = int(input("Enter the starting page to process: "))
    end_page = int(input("Enter the ending page to process: "))

    # Process the image
    loop = 0
    # Loop many times on the same image will result in better deskew
    while loop < 3:
        if loop != 0:
            image_folder = output_folder

        for i in range(start_page, end_page + 1):
            image_file_path = f"{image_folder}\\{pdf_name}_page{i:03}.png"
            output_path = f"{output_folder}\\{pdf_name}_page{i:03}.png"
            if (not os.path.exists(image_file_path)):
                print(f"[+] {image_file_path} not existed")
                continue
            # Example usage
            deskew_image(image_file_path, output_path)
        loop += 1


if __name__ == "__main__":
    main()

