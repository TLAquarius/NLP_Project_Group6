from paddleocr import PaddleOCR, draw_ocr
import cv2
import matplotlib.pyplot as plt
import os

# Đường dẫn tới mô hình ch_PP-OCRv4
ocr = PaddleOCR(det_model_dir='./det/final_det_inference',  # Model detection
                rec_model_dir='./rec/ch_PP-OCRv3_rec_infer',  # Model recognition
                use_gpu=False)  # Đặt True nếu sử dụng GPU

# Đường dẫn tới ảnh chữ Nôm để kiểm tra
image_path = './DVSKTT_thu_I_1a.jpg'

# Kiểm tra ảnh
assert os.path.exists(image_path), f"Image not found at {image_path}"
image = cv2.imread(image_path)

# OCR: Phát hiện và nhận diện văn bản
results = ocr.ocr(image_path, cls=False)

# Kiểm tra kết quả OCR
if results is None or not results[0]:
    print("No text detected or OCR failed.")
else:
    # Hiển thị kết quả
    for line in results[0]:
        print(f"Detected text: {line[1][0]}, Confidence: {line[1][1]:.2f}")

    # Vẽ kết quả lên ảnh
    boxes = [item[0] for item in results[0]]  # Vùng phát hiện văn bản
    txts = [item[1][0] for item in results[0]]  # Văn bản nhận diện
    scores = [item[1][1] for item in results[0]]  # Độ tin cậy

    # Kiểm tra font
    font_path = './NomNatong-Regular.ttf'
    assert os.path.exists(font_path), "Font file not found"

    # Sử dụng PaddleOCR để vẽ
    image_with_results = draw_ocr(image, boxes, txts, scores, font_path=font_path)

    # Hiển thị ảnh kết quả
    plt.figure(figsize=(10, 10))
    plt.imshow(image_with_results)
    plt.axis('off')
    plt.show()