# Python OCR API

This project provides a simple API for Optical Character Recognition (OCR) using Python. It allows users to upload images and receive extracted text along with confidence scores.

## Project Structure

```
python-api-project
├── src
│   ├── api.py        # API implementation
│   ├── test.py       # OCR processing code
│   └── utils.py      # Utility functions
├── requirements.txt   # Project dependencies
└── README.md          # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd python-api-project
   ```

2. **Install dependencies:**
   Ensure you have Python 3.6 or higher installed. Then, run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the API:**
   You can start the API by running:
   ```
   python src/api.py
   ```

   The API will be available at `http://localhost:8000`.

## Usage

To use the API, send a POST request to the `/ocr` endpoint with an image file. You can use tools like `curl` or Postman.

### Example using `curl`:

```bash
curl -X POST "http://localhost:8000/ocr" -F "file=@path_to_your_image.jpg"
```

### Response

The API will return a JSON response containing the detected text and confidence scores:

```json
{
  "results": [
    {
      "text": "Detected text",
      "confidence": 0.95
    },
    ...
  ]
}
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.