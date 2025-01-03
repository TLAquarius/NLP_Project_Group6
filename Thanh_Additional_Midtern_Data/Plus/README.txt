- Chú thích các file và trình tự sử dung:
 ++++++++++++++++++++++++++++++++++++++++
[+] image_extracting.py: code để trích xuất các ảnh chứa chữ Quốc Ngữ và Hán Nôm.
	+ Có thể điều chỉnh lại đường dẫn đến file PDF cho phù hợp
	+ Có thể điều chỉnh lại đường dẫn đến thư mục output của Quốc Ngữ và Hán Nôm cho phù hợp.
	+ Ở các vị trí yêu cầu input PDF page thì đó là phạm vi các trang trong PDF sẽ được trích xuất.
	+ Ở các vị trí yêu cầu input trang bắt đầu và kết thúc thật thì nhập số trang bắt đầu và kết thúc được ghi trong sách (đối với trang chữ nôm, do được đọc ngược, nên khi input ta vẫn sẽ input theo đúng thứ tự đọc. Ví dụ trang Hán-Nôm bắt đầu từ trang 400 đến 100 thì ta nhập input trang bắt đầu = 400 và kết thúc = 100)
	+ Ở đầu của code có phần ignore, đó là biến để bỏ qua việc trích xuất một số trang ngoại lệ.
[+] image_shadow_remove.py: code để giảm hoàn toàn bóng cũng như làm rõ ảnh.
	+ Có thể điều chỉnh thư mục input/output.
	+ Có thể chạy ngay sau image_extracting.py.
[+] semi_auto_crop_image.py: code để cắt nhiều ảnh cùng đồng thới với điều chỉnh tùy ý.
	+ Tên file phải cùng tên file PDF và có định dạng "<tên file PDF>_pageXXX.png"
	+ Có thể điều chỉnh thư mục input/output phù hợp.
	+ Có thể chạy ngay sau image_extracting.py.
	+ Việc cắt ảnh là tương đối thủ công do các ảnh nằm ở các vị trí lệch nhau ngẫu nhiên nên rất khó xử lý hoàn toàn tự động.
	+ Code chủ yếu sẽ cho phép cắt ảnh cùng lúc tùy theo mode. Vì thường các trang chẵn/lẻ thường có format, độ lệch khá tương đồng nhau, nên em đã chia thành các mode:
		* Mode 1: cùng lúc cắt tất cả các ảnh từ trang x tới trang y.
		* Mode 2: cùng lúc cắt tất cả các ảnh có số trang CHẴN từ trang x đến trang y.
		* Mode 3: cùng lúc cắt tất cả các ảnh có số trang LẺ từ trang x đến trang y.
		* Mode 4: cắt 1 trang cụ thể.
[+] image_deskewed.py: code để xoay ảnh được ngay ngắn. Chỉ được dùng với các ảnh Hán Nôm.
	+ Chỉ nên dùng sau khi đã xử loại bỏ bóng, cắt ảnh.
	+ Có thể điều chỉnh thưc mục input/output.
[+] Quoc_Ngu_ocr.py: code trích xuất phần text của ảnh Quốc Ngữ, sử dụng Google Vision API.
	+ Thư mục ảnh input cần là ảnh đã qua xử lý (cắt và loại bỏ bóng) để cho kết quả tốt nhất.
[+] Han_Nom_ocr.py: code trích xuất chữ Hán Nôm sử dụng CLC API và lưu vào file .json.
	+ Thư mục ảnh input cần là ảnh đã qua các bước xử lý cần thiết để cho kết quả tốt nhất.
[+] convert_output.py: thực hiện dóng hàng các box OCR và xuất file output excel.
	+ Cần thư mục output của Quoc_Ngu_ocr.py và Han_Nom_ocr.py.
	+ Sẽ cho input phạm vi trang cần xuất file excel.
	+ Tên file excel sẽ mặc định là tên của PDF. Có thể thay đổi tên file excel tại "SPECIFY THE NAME AND PATH ON OUTPUT EXCEL FILE" trong hàm writeExcel.

=====================================================
*****************UPDATE ĐỢT NỘP 2********************
=====================================================
[+] convert_output.py:
	+ Code xử lý giờ đây sẽ tự động lấy toàn bộ file json chứa kết quả OCR Hán-Nôm lưu trong thư mục chứa kết quả OCR CLC API.
	+ Không còn cần liệt kê số trang phải xử lý.
	+ Thêm phần code loại bỏ những box có độ confidence < 0.55.
	+ Loại bỏ những box màu xanh lá.