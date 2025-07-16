from flask import Flask, request, jsonify
import numpy as np
import cv2
import base64
import requests
import tempfile
import os
import time
import json
import asyncio
import glob

from paddleocr import PaddleOCR

app = Flask(__name__)


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

# Sample data (in a real application, this would come from a database)
data = {
    "items": [
        {"id": 1, "name": "Apple"},
        {"id": 2, "name": "Banana"}
    ]
}



# extract all ocr results
all_receipt_urls = []

async def wait_for_file(filepath, timeout=5):
    """Wait until the file exists and is readable."""
    start = time.time()
    while not (os.path.exists(filepath) and os.path.getsize(filepath) > 0):
        await asyncio.sleep(0.1)
        if time.time() - start > timeout:
            raise TimeoutError(f"Timeout waiting for file {filepath}")


# from ocr results from paddle & saved to json, extract data & pair it with its correspondence url
def extract_data_from_json(json_file_path, item):
    # print(json_file_path)
    # print(url)
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    rec_texts = data.get("rec_texts", [])
    rec_scores = data.get("rec_scores", [])
    if rec_scores:
        average = sum(rec_scores) / len(rec_scores)
        rounded_average = round(average, 2)
    else:
        rounded_average = 0.0  # or handle as needed

    updatedItem = {
                    **item,
                    "text": ' '.join(rec_texts),
                    "confidence": rounded_average,
                }
    print(updatedItem)
    all_receipt_urls.append(updatedItem)

# Visualize the results and save the JSON results
async def image_ocr_process(ocrImage, item):
    print(ocrImage)
    print(item)
    ocrResult = ocr.predict(input=ocrImage)
    for res in ocrResult:
        res.save_to_json("ocr_output")
        file_name = os.path.basename(ocrImage)
        json_file_path = f"ocr_output/{file_name}".replace(".jpeg", "_res.json")

        await wait_for_file(json_file_path)  # 🕒 Wait for the file to be written
        extract_data_from_json(json_file_path, item)



# accessing item {"recept": ""}
async def process_temp_file_from_url(item):
    # Step 1: Download and save to a temp file
    response = requests.get(item['receipt'])
    print(item['receipt'])
    response.raise_for_status()

    # save the url image in a temp file with .jpeg suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp_file:
        tmp_file.write(response.content)
        temp_path = tmp_file.name

    try:
        # Step 2: Use the file (pass to another function or process)
        print(f"Temp file saved at: {temp_path}")
        await image_ocr_process(temp_path, item)

        # await asyncio.sleep(7)  # wait for 7 seconds
        # file_name = os.path.basename(temp_path)
        # json_file_path = f"ocr_output/{file_name}"
        # json_filename = json_file_path.replace(".jpeg", "_res.json")
        # extract_data_from_json(json_filename, item)

    finally:
        # Step 3: Clean up the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Deleted temp file: {temp_path}")



# looping each item [{"recept": ""}, {"recept": ""}]
async def enrich_urls(urls):
  for item in urls:
    await process_temp_file_from_url(item)


def save_to_file(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



# image_list = [{'receipt': "https://bayafleet-driver-prod-asset-lib.s3.ap-southeast-1.amazonaws.com/attachment/receipt/1746409184370-Driver-Fadhlur-RahmanbinMohdGhazali"}, {'receipt': "https://bayafleet-driver-prod-asset-lib.s3.ap-southeast-1.amazonaws.com/attachment/receipt/1745543891140-Driver-SARAVANAN-ALGOVINDASAMY"}]
# OUTPUT_JSON = 'output.json'


@app.route('/paddle-process-image', methods=['POST'])
async def main():
    if request.is_json and 'receipt_list' in request.json:
        receipt_list = request.json['receipt_list']
        try:
            await enrich_urls(receipt_list) # do ocr, extract ocr result & put in the all_receipt_urls array
            print(f"✅ Done: {len(all_receipt_urls)} receipts processed.")
            # todo - clear ocr_output directory & output.json file before every successful return
            return jsonify({
                'message': 'Image processed successfully',
                'all_receipt_urls': all_receipt_urls
            }), 200
        except Exception as e:
            return jsonify({'error': f'Error fetching image from URL: {str(e)}'}), 400

    else:
        return jsonify({'error': 'No image file or image URL provided'}), 400
        




def clear_ocr_output(directory='ocr_output'):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    files = glob.glob(os.path.join(directory, '*'))
    for file_path in files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
@app.route('/reset_output', methods=['GET'])
def reset_output():
    clear_ocr_output()
    return jsonify({'message': 'ocr_output directory cleared'}), 200





@app.route('/ping', methods=['GET'])
def get_items():
    return jsonify("Server is running normally.")

if __name__ == '__main__':
    app.run(debug=True)