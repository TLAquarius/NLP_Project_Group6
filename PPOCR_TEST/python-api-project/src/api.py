from test import process_image  
from flask import Flask, request, jsonify
from PIL import Image
import base64
from io import BytesIO


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)