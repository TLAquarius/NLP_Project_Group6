from PIL import Image
import os

def crop_image(image_file_path, output_path, up_bound, low_bound, left_bound, right_bound):
    '''
    Crop image base on the portion of upper/lower/left/right bound

    Parameters
    ----------
        image_file_path: str
            Path to the image need to be cropped
        output_path: str
            Path to the output
        up_bound: int
            The upper portion to be cut
        low_bound: int
            The lower portion to be cut
        left_bound: int
            The left portion to be cut
        right_bound: int
            The right portion to be cut
    Returns
    -------
    '''

    try:
        # Open the image using Pillow
        img_pil = Image.open(image_file_path)

        # Crop the image using the specified area
        width, height = img_pil.size

        cropped_img = img_pil.crop((0 if left_bound == 0 else width//left_bound,
                                   0 if up_bound == 0 else height//up_bound,
                                   width - (0 if right_bound == 0 else width//right_bound),
                                   height - (0 if low_bound == 0 else height//low_bound)))
        # Save the cropped image
        cropped_img.save(output_path)
        print(f"Cropped image saved at: {output_path}")

    except Exception as e:
        print(f"Error processing the image: {e}")


def main():
    # Input folder paths to the shadow removed images (change base on user)
    image_folder = "Han-Nom_image_khanh_preprocess"

    # Output folder paths (change base on user)
    output_folder = image_folder
    os.makedirs(output_folder, exist_ok=True)

    # The PDF file name
    pdf_name = "Sách Nôm công giáo 1995 - 110 - Tu Nguyen Yeu Ly - Phan II"
    mode = int(input("Mode:\n"
                     "1. All page from page 'a' to 'b'\n"
                     "2. Even page from page 'a' to 'b'\n"
                     "3. Odd page from page 'a' to 'b'\n"
                     "4. Single page\n"
                     "Enter mode: "))

    start_page = 0
    end_page = 0
    if mode == 4:
        start_page = end_page = int(input("Enter page number want to be cropped: "))
    else:
        start_page = int(input("Enter start page 'a': "))
        end_page = int(input("Enter end page 'b': "))

    # Cut 1/up_bound from the upper edge of image
    up_bound = int(input("Enter upper bound portion: "))

    # Cut 1/low_bound from the lower edge of image
    low_bound = int(input("Enter low bound portion: "))

    # Cut 1/left_bound from the left edge of image
    left_bound = int(input("Enter left bound portion: "))

    # Cut 1/right_bound from the right edge of image
    right_bound = int(input("Enter right bound portion: "))

    # Call the crop_image function to crop and save the image
    for i in range(start_page, end_page + 1):
        image_file_path = f"{image_folder}\\{pdf_name}_page{i:03}.png"
        output_folder_path = f"{output_folder}\\{pdf_name}_page{i:03}.png"
        if (not os.path.exists(image_file_path)):
            print(f"[+] {image_file_path} not existed")
            continue

        if mode == 1 or mode == 4:
            crop_image(image_file_path, output_folder_path, up_bound, low_bound, left_bound, right_bound)
        elif i % 2 == 0 and mode == 2:
            crop_image(image_file_path, output_folder_path, up_bound, low_bound, left_bound, right_bound)
        elif i % 2 != 0 and mode == 3:
            crop_image(image_file_path, output_folder_path, up_bound, low_bound, left_bound, right_bound)


# Run the main function
if __name__ == "__main__":
    main()
