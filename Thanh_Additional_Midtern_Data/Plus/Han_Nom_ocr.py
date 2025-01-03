import requests
import json
import os

def upload_image(file_path):
    '''
    Upload the image need to be OCR-ed by CLC API

    Parameters
    ----------
        file_path: str
            Path to the image need to be OCR
    Returns
    -------
    '''

    url = "https://tools.clc.hcmus.edu.vn/api/web/clc-sinonom/image-upload"
    headers = {"User-Agent": "test 121113"}

    try:
        with open(file_path, 'rb') as f:
            files = {'image_file': (os.path.basename(file_path), f, 'image/png')}  # Assuming JPEG
            response = requests.post(url, headers=headers, files=files)

            response.raise_for_status()  # Raise an exception for bad status codes
            return response
    except requests.exceptions.RequestException as e:
        print(f"Error uploading image: {e}")
        return None

def send_ocr_request(file_path):
    '''
    Request the OCR of the image by CLC API

    Parameters
    ----------
        file_path: str
            The name of the uploaded image
    Returns
    -------
    '''

    url = "https://tools.clc.hcmus.edu.vn/api/web/clc-sinonom/image-ocr"
    headers = {"User-Agent":"test 121113"}
    data = {
        "ocr_id": 1,
        "file_name": file_path
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None

def save_response_to_json(response_data, file_path):
    '''
    Save OCR response to .json file

    Parameters
    ----------
        response_data:
            OCR response from the CLC API
        file_path: str
            Path to output folder
    Returns
    -------
    '''

    file_name, _ = os.path.splitext(file_path)
    json_file_path = f"{file_name}.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        print(f"Response saved to: {json_file_path}")
    except Exception as e:
        print(f"Error saving response to JSON: {e}")

if __name__ == "__main__":

    start_page = int(input("Please enter the starting page number of Han-Nom want to ocr: "))

    end_page = int(input("Please enter the real ending page number of Han-Nom: "))
    pdf_name = "Sách Nôm công giáo 1995 - 110 - Tu Nguyen Yeu Ly - Phan II"

    # Path to the folder contain all preprocessed Han-Nom images
    han_nom_image_folder = "D:\\PycharmProjects\\NLP_GK_22127392\\Han-Nom_image_khanh_preprocess"

    # Path to the OCR json output folder
    output_folder = "Han-Nom_ocr"
    os.makedirs(output_folder, exist_ok=True)

    for i in range(start_page, end_page+1):
        image_file_path = f"{han_nom_image_folder}\\{pdf_name}_page{i:03}.png"
        output_path = f"{output_folder}\\{pdf_name}_page{i:03}"
        if(not os.path.exists(image_file_path)):
            print(f"[+] {image_file_path} not existed")
            continue
        response_upload = upload_image(image_file_path)
        response_upload_data = response_upload.json()
        file_name = response_upload_data["data"]["file_name"]
        response_data = send_ocr_request(file_name)

        if response_data:
            save_response_to_json(response_data, output_path)