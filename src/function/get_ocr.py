import requests
import tempfile
import os
import time
import json
import asyncio

from paddleocr import PaddleOCR

from src.function.get_trxn import get_trx_details


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)


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
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    rec_texts = data.get("rec_texts", [])
    joinedTexts = ' '.join(rec_texts)

    rec_scores = data.get("rec_scores", [])
    if rec_scores:
        average = sum(rec_scores) / len(rec_scores)
        rounded_average = round(average, 2)
    else:
        rounded_average = 0.0  # or handle as needed

    ocr_details = get_trx_details(joinedTexts)
    updatedItem = {
                    **item,
                    "text": joinedTexts,
                    "confidence": rounded_average,
                    "ocr_details": ocr_details,
                }
    return updatedItem
    # print(updatedItem)
    # updated_receipts_urls.append(updatedItem)

# Visualize the results and save the JSON results
async def image_ocr_process(ocrImage, item):
    # print(ocrImage)
    # print(item)
    ocrResult = ocr.predict(input=ocrImage)
    for res in ocrResult:
        res.save_to_json("ocr_output")
        file_name = os.path.basename(ocrImage)
        json_file_path = f"ocr_output/{file_name}".replace(".jpeg", "_res.json")

        await wait_for_file(json_file_path)  # 🕒 Wait for the file to be written
        updatedItem = extract_data_from_json(json_file_path, item)
        return updatedItem



# accessing item {"recept": ""}
async def process_temp_file_from_url(item):
    # Step 1: Download and save to a temp file
    response = requests.get(item['receipt'])
    # print(item['receipt'])
    response.raise_for_status()

    # save the url image in a temp file with .jpeg suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp_file:
        tmp_file.write(response.content)
        temp_path = tmp_file.name

    try:
        # Step 2: Use the file (pass to another function or process)
        # print(f"Temp file saved at: {temp_path}")
        updatedItem = await image_ocr_process(temp_path, item)

    finally:
        # Step 3: Clean up the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            # print(f"Deleted temp file: {temp_path}")
        return updatedItem



# looping each item [{"recept": ""}, {"recept": ""}]
async def enrich_urls(urls):
    all_receipt_urls = []
    for item in urls:
        updatedItem = await process_temp_file_from_url(item)
        all_receipt_urls.append(updatedItem)
    
    return all_receipt_urls


def save_to_file(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
