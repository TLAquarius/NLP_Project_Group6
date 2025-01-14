from test import process_image, export_result
from flask import Flask, request, jsonify, send_file
from PIL import Image
import base64
from io import BytesIO
import io


app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Ensure the temp directory exists
        print("Hello, world!")

        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image = Image.open(image_file).convert('RGB')

        result = process_image(image)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['POST'])
def EmptyAPI():
    return jsonify({
            'result': 'connect successfully',
        })

@app.route('/download-txt', methods=['POST'])
def download_txt():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image = Image.open(image_file).convert('RGB')
        result = export_result(image)
        
        file_stream = io.StringIO()
        file_stream.write(image_file.filename)
        file_stream.write('\t')
        file_stream.write(str(result))
        file_stream.seek(0)

        return send_file(
            io.BytesIO(file_stream.getvalue().encode('utf-8')),  # Convert to bytes
            as_attachment=True,  # Enable download
            download_name="Label.txt",  # File name for download
            mimetype="text/plain"  # File type
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)