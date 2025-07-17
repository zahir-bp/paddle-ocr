from flask import Flask, request, jsonify
import requests
import json
import tempfile
import os
import time
import asyncio

# import sys
# import os

# # Add the 'src' folder to the Python path
# sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.function.get_ocr import enrich_urls
from src.function.clear_output import clear_ocr_output

app = Flask(__name__)


# Sample data (in a real application, this would come from a database)
data = {
    "items": [
        {"id": 1, "name": "Apple"},
        {"id": 2, "name": "Banana"}
    ]
}


@app.route('/paddle-process-image', methods=['POST'])
async def paddle_ocr():
    if request.is_json and 'receipt_list' in request.json:
        receipt_list = request.json['receipt_list']
        try:
            all_receipt_urls = await enrich_urls(receipt_list) # do ocr, extract ocr result & put in the all_receipt_urls array
            # print(f"✅ Done: {len(all_receipt_urls)} receipts processed.")
            # todo - clear ocr_output directory & output.json file before every successful return
            return jsonify({
                'message': 'Image processed successfully',
                'all_receipt_urls': all_receipt_urls
            }), 200
        except Exception as e:
            return jsonify({'error': f'Error fetching image from URL: {str(e)}'}), 400

    else:
        return jsonify({'error': 'No image file or image URL provided'}), 400
        



@app.route('/reset_output', methods=['GET'])
def reset_output():
    clear_ocr_output()
    return jsonify({'message': 'ocr_output directory cleared'}), 200




@app.route('/ping', methods=['GET'])
def get_items():
    return jsonify("Server is running normally.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)