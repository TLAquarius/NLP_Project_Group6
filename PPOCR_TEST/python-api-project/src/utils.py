def preprocess_image(image):
    # Function to preprocess the image before OCR
    # This can include resizing, converting to grayscale, etc.
    return image

def save_uploaded_file(uploaded_file, save_path):
    # Function to save the uploaded file to a specified path
    with open(save_path, 'wb') as f:
        f.write(uploaded_file.read())

def validate_image_file(file):
    # Function to validate the uploaded file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in file.name and file.name.rsplit('.', 1)[1].lower() in allowed_extensions