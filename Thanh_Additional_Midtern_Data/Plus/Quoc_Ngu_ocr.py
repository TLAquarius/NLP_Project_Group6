from google.cloud import vision
import re
import os
import cv2

json_key_path = "glowing-cooler-441113-m8-98ea36811795.json" # Change with your Google Cloud Vision API key json file

"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""
def setup_google_credentials(json_key_path):
    """
    Set the Google Application Credentials environment variable.
    Args:
        json_key_path (str): Path to the JSON key file for Google Cloud Vision API.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path

def google_ocr(file, output_folder_path):
    '''
    Get the Quoc Ngu text from the Quoc Ngu image and store as full text (_text.txt) and word by word (_word.txt)

    Parameters
    ----------
        file: str
            Path to the image need to be OCR
        folder_path: str
            Path to the output folder
    Returns
    -------
    '''
    word_text = []
    print(f"[+] Extracting text from {file}...")
    file_name = os.path.basename(file)
    file_name = os.path.splitext(file_name)[0]
    word_text_file = output_folder_path + '\\' + file_name.rsplit('.', maxsplit=2)[0] + "_word.txt"
    full_text_file = output_folder_path + '\\' + file_name.rsplit('.', maxsplit=2)[0] + "_text.txt"
    try:
        # Initialize the Vision API client
        client = vision.ImageAnnotatorClient()

        # Read the image file into memory
        with open(file, "rb") as image_file:
            content = image_file.read()

        # Prepare the image for the Vision API
        image = vision.Image(content=content)
        # Set language hint to Vietnamese
        image_context = vision.ImageContext(language_hints=["vi"])

        # Perform text detection
        response = client.text_detection(image=image, image_context=image_context)
        texts = response.text_annotations

        # Process and print the detected text
        if texts:
            page_text = texts[0].description

            # Clean and process text
            # Replace multiple spaces with a single space
            page_text = re.sub(r' +', ' ', page_text)

            # Remove digits
            page_text = re.sub(r'\d', '', page_text)

            # Remove text within parentheses (including the parentheses themselves)
            page_text = re.sub(r'\(.*?\)', '', page_text, flags=re.DOTALL)

            # Replace specific terms
            page_text = re.sub(r'\bGiêsu\b', 'Giê su', page_text)
            page_text = re.sub(r'\bv\.v\b', 'vân vân', page_text)

            # Add spaces around hyphens
            page_text = re.sub(r'-', ' - ', page_text)

            # Add spaces around punctuation
            page_text = re.sub(r'([.,!?;:])', r' \1 ', page_text)
            page_text = page_text.splitlines()
            page_text = [line.strip() for line in page_text if line.strip()]
            page_text = [line for line in page_text if not (line.strip()).isdigit()]
            page_text = [line for line in page_text if re.search(r'[a-zA-Z]', line)]


            for line in page_text:
                line = line.lower()
                line = re.sub(r'\bgiêsu\b', 'giê su', line)
                word_text.append(re.findall(r'\b\w+\b', line))

            # Save word-by-word text
            with open(word_text_file, "w", encoding="utf-8") as pt_file:
                for line in word_text:
                    pt_file.write(" ".join(line) + "\n")
            print(f"[+] Done extracting word by word and saved to {word_text_file}")

            # Save full text with page numbers
            with open(full_text_file, "w", encoding="utf-8") as ft_file:
                for line in page_text:
                    ft_file.write(line + "\n")
            print(f"[+] Done extracting sentences with page numbers and saved to {full_text_file}")
            # The first result contains all detected text
        else:
            print("No text detected in the image.")

        # Check for errors in the response
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Set up Google Cloud Vision credentials
    setup_google_credentials(json_key_path)

    # Input image folder (the folder contain the all processed Quoc-Ngu images)
    input_folder = "Quoc-Ngu_image_khanh_preprocess"

    # Output folder
    output_folder = "Quoc-Ngu_text_khanh"
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input folder
    for file in os.listdir(input_folder):
        # Construct the full file path
        file_path = os.path.join(input_folder, file)

        # Check if it is an image file (you can add more extensions if needed)
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
            # Perform OCR on the image
            google_ocr(file_path, output_folder)

if __name__ == "__main__":
    main()
