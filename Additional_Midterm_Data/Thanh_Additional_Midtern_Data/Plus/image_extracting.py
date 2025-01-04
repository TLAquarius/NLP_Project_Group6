import fitz
import os
from PIL import Image
from google.cloud import vision
from io import BytesIO
import cv2
import numpy as np
import string

# PDF page number to be exclude from extracting
ignore_pdf = [36]

# Real book page number to be exclude from extracting
ignore_real_page = [189]

# Json file store the key for Google Vision API
credentials_path = "glowing-cooler-441113-m8-98ea36811795.json"

def reduce_shadow(image):
    '''
    Reduce shadow in image (increase a bit the contrast)

    Parameters
    ----------
        image: image
            The image needed to be reduce shadow
    Returns
        shadow_reduced_image: Image
            The reduced shadow image
    -------
    '''
    # Convert PIL image to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Use a large kernel to estimate the shadow
    dilated_img = cv2.dilate(gray, np.ones((15, 15), np.uint8))
    blurred_img = cv2.medianBlur(dilated_img, 51)

    # Blend the original image with the shadow-reduced version
    shadow_reduced = cv2.addWeighted(gray, 0.95, blurred_img, 0.28, 0)

    # Normalize the image for improved visibility
    norm_img = cv2.normalize(shadow_reduced, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    # Convert back to PIL Image
    shadow_reduced_image = Image.fromarray(norm_img)
    return shadow_reduced_image

def preprocess_image(image, target_size):
    '''
    Resize to about fix size and reduce shadow of image

    Parameters
    ----------
        image:
            The image
        target_size: tuple
            The target size of the image
    Returns
        image:
            The image after resize and reduce shadow
    -------
    '''
    # Resize the image to the target size
    image = image.resize(target_size, Image.LANCZOS)
    # Remove shadows
    image = reduce_shadow(image)
    return image

def find_gutter_column(image):
    '''
    Detect/estimate the gutter line of the book base on projection

    Parameters
    ----------
        image:
            The image
    Returns
        gutter_column: int
            The pixel column index which maybe the gutter
    -------
    '''
    # Convert the PIL image to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to smooth the image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform binary thresholding to highlight potential gutter lines
    _, binary = cv2.threshold(blurred, 160, 255, cv2.THRESH_BINARY_INV)

    # Calculate the vertical projection (sum of pixel values along each column)
    projection = np.sum(binary, axis=0)

    # Normalize the projection for better visualization
    projection = projection / np.max(projection)

    # Define the range for columns (1/3 to 2/3 of the image width)
    height, width = gray.shape
    start_col = width // 3
    end_col = 2 * width // 3

    # Get the columns within the defined range
    projection_range = projection[start_col:end_col]

    # Find the columns with the highest projection values
    top_columns = np.argsort(projection_range)[-100:]  # Get the top 10 columns in the range

    # Adjust the column indices to match the full image width
    top_columns = top_columns + start_col

    # Calculate gutter column as the average of the smallest and largest indices in top_columns
    min_top_column = np.min(top_columns)
    max_top_column = np.max(top_columns)
    gutter_column = (min_top_column + max_top_column) // 2

    return gutter_column

def process_quoc_ngu_images(pdf_path, quoc_ngu_folder, start_page, end_page, credentials_path, real_start_page,
                            real_end_page):
    '''
    Extract from the PDF and split roughly the Quoc Ngu pages images

    Parameters
    ----------
        pdf_path: str
            Path to PDF file
        quoc_ngu_folder: str
            Path to folder to store Quoc Ngu output images
        start_page: int
            Starting page number of PDF want to extract
        end_page: int
            Ending page number of PDF want ot extract
        credentials_path: str
            The path to Google API key
        real_start_page: int
            Starting page number of the real book want to extract
        real_end_page: int
            Ending page number of the real book want to extract
    Returns
        page_mapping: list
            List of real book pages the Quoc Ngu extracted from
    -------
    '''
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    client = vision.ImageAnnotatorClient()
    pdf_document = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    page_mapping = []

    first_image_size = None

    for pdf_page_num in range(start_page - 1, end_page):  # Pages are 0-indexed
        if pdf_page_num in ignore_pdf:
            continue
        page = pdf_document[pdf_page_num]
        images = page.get_images(full=True)

        if not images:
            print(f"No images found on PDF page {pdf_page_num + 1}.")
            continue

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(BytesIO(image_bytes))

            # Determine target size based on the first image
            if first_image_size is None:
                first_image_size = image.size  # (width, height)

            # Preprocess the image
            image = preprocess_image(image, first_image_size)

            # Rotate 90 degrees clockwise
            image = image.rotate(-90, expand=True)

            '''
            ----------------------------
            Split into left and right halves (Change the number base on the pages layout)
            ----------------------------
            '''
            width, height = image.size
            left_part = image.crop((0, 0, width // 2 + width // 250, height))
            right_part = image.crop((width // 2 - width // 50 - 20, 0, width - width // 20, height))


            # OCR for page numbers
            left_numbers = detect_numbers_with_google_vision(left_part, client)

            left_current = int(max((x for x in left_numbers if real_end_page >= int(x) >= real_start_page), default=-1))
            right_current = left_current + 1

            # Save left and right images
            if left_current <= real_end_page and left_current != -1\
                and left_current not in ignore_real_page:
                left_image_name = f"{pdf_name}_page{left_current-real_start_page+1:03}.png"
                left_part.save(os.path.join(quoc_ngu_folder, left_image_name))
                page_mapping.append(left_current-real_start_page+1)

            if right_current <= real_end_page and right_current != -1\
                and right_current not in ignore_real_page:
                right_image_name = f"{pdf_name}_page{right_current-real_start_page+1:03}.png"
                right_part.save(os.path.join(quoc_ngu_folder, right_image_name))
                page_mapping.append(right_current-real_start_page+1)

        print(f"Finished processing Quoc Ngu page: {pdf_page_num + 1}")
    return page_mapping

def process_han_nom_images(pdf_path, han_nom_folder, start_page, end_page, credentials_path, real_start_page,
                            real_end_page, pairing_dict):
    '''
    Extract from the PDF and split roughly the Han-Nom pages images

    Parameters
    ----------
        pdf_path: str
            Path to PDF file
        han_nom_folder: str
            Path to folder to store Han-Nom output images
        start_page: int
            Starting page number of PDF want to extract
        end_page: int
            Ending page number of PDF want ot extract
        credentials_path: str
            The path to Google API key
        real_start_page: int
            Starting page number of the real book want to extract
        real_end_page: int
            Ending page number of the real book want to extract
    Returns
    -------
    '''
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    client = vision.ImageAnnotatorClient()
    pdf_document = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    first_image_size = None

    for pdf_page_num in range(start_page - 1, end_page):  # Pages are 0-indexed
        if pdf_page_num in ignore_pdf:
            continue
        page = pdf_document[pdf_page_num]
        images = page.get_images(full=True)

        if not images:
            print(f"No images found on PDF page {pdf_page_num + 1}.")
            continue

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(BytesIO(image_bytes))

            # Determine target size based on the first image
            if first_image_size is None:
                first_image_size = image.size  # (width, height)

            # Rotate 90 degrees clockwise
            image = image.rotate(-90, expand=True)

            # Split into left and right halves
            gutter_column = find_gutter_column(image)
            width, height = image.size

            left_part = image.crop((0, 0, gutter_column, height))
            left_part = preprocess_image(left_part, first_image_size)

            right_part = image.crop((gutter_column, 0, width, height))
            right_part = preprocess_image(right_part, first_image_size)

            # OCR for page numbers
            left_numbers = detect_numbers_with_google_vision(left_part, client)

            left_current = int(max((x for x in left_numbers if real_end_page <= int(x) <= real_start_page), default=-1))
            right_current = left_current + 1

            # Save left and right images
            if (left_current >= real_end_page and left_current != -1
                    and (abs(left_current-real_start_page)+1) in pairing_dict)\
                    and left_current <= real_start_page\
                    and left_current not in ignore_real_page:
                left_image_name = f"{pdf_name}_page{abs(left_current-real_start_page)+1:03}.png"
                left_part.save(os.path.join(han_nom_folder, left_image_name))

            if (right_current >= real_end_page and right_current != -1
                    and (abs(right_current-real_start_page)+1) in pairing_dict)\
                    and right_current <= real_start_page\
                    and right_current not in ignore_real_page:
                right_image_name = f"{pdf_name}_page{abs(right_current-real_start_page)+1:03}.png"
                right_part.save(os.path.join(han_nom_folder, right_image_name))

        print(f"Finished processing Han-Nom page: {pdf_page_num + 1}")

def detect_numbers_with_google_vision(image, client):
    '''
    Extract from the PDF and split roughly the Quoc Ngu pages images

    Parameters
    ----------
        image:
            The image to OCR with Google Vision API
        client:
            Google Vision API init
    Returns
        numbers: list
            The real book page number OCR-ed
    -------
    '''
    width, height = image.size

    # Change the region normally contain the page number
    top_region = image.crop((width//7, 0, width - width//3.2, height // 5))

    buffered = BytesIO()
    top_region.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()
    vision_image = vision.Image(content=image_bytes)
    response = client.text_detection(image=vision_image)
    texts = response.text_annotations

    if texts:
        detected_text = texts[0].description
        cleaned_text = "".join(char for char in detected_text if char not in string.punctuation)
        numbers = ["".join(filter(str.isdigit, word)) for word in cleaned_text.split() if any(char.isdigit() for char in word)]
        return numbers
    return []

def main():
    print("PDF to Real Book Page Splitter")

    # PDF file name
    pdf_path = "Sách Nôm công giáo 1995 - 100 - Tu Chung Luoc Thuyet.pdf"

    # Folder to store the Quoc-Ngu images
    quoc_ngu_folder = "Quoc-Ngu_image"
    os.makedirs(quoc_ngu_folder, exist_ok=True)

    #Folder to store the Han-Nom images
    han_nom_folder = "Han-Nom_image"
    os.makedirs(han_nom_folder, exist_ok=True)

    quoc_ngu_start_page = int(input("Starting PDF page number for Quốc Ngữ: "))
    quoc_ngu_end_page = int(input("Ending PDF page number for Quốc Ngữ: "))
    quoc_ngu_start_page_real = int(input("Starting book page number for Quốc Ngữ: "))
    quoc_ngu_end_page_real = int(input("Ending book page number for Quốc Ngữ: "))

    han_nom_start_page = int(input("Starting PDF page number for Hán-Nôm: "))
    han_nom_end_page = int(input("Ending PDF page number for Hán-Nôm: "))
    han_nom_start_page_real = int(input("Starting book page number for Hán-Nôm: "))
    han_nom_end_page_real = int(input("Ending book page number for Hán-Nôm: "))

    # Extracting the Quoc-Ngu
    page_pairing_dict = process_quoc_ngu_images(pdf_path, quoc_ngu_folder, quoc_ngu_start_page, quoc_ngu_end_page,
                                                credentials_path, quoc_ngu_start_page_real, quoc_ngu_end_page_real)

    # Extracting the Han-Nom base on the corresponded Quoc-Ngu pages
    process_han_nom_images(pdf_path, han_nom_folder, han_nom_start_page, han_nom_end_page,
                           credentials_path, han_nom_start_page_real, han_nom_end_page_real, page_pairing_dict)


if __name__ == "__main__":
    main()
