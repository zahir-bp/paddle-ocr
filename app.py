from flask import Flask, jsonify, request
import cv2
import numpy as np

app = Flask(__name__)

# Sample data (in a real application, this would come from a database)
data = {
    "items": [
        {"id": 1, "name": "Apple"},
        {"id": 2, "name": "Banana"}
    ]
}


@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    
    # Read the image using OpenCV
    nparr = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Could not decode image'}), 400

    # Example: Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Example: Perform some processing (e.g., edge detection)
    edges = cv2.Canny(gray_img, 100, 200)

    # Encode the processed image for response
    _, buffer = cv2.imencode('.png', edges)
    processed_image_base64 = np.array(buffer).tobytes() # You might want to base64 encode this for JSON response

    return jsonify({'message': 'Image processed successfully', 'processed_image_data': '...'}), 200 # Replace '...' with base64 encoded image


@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(data["items"])

@app.route('/api/post/items', methods=['POST'])
def add_item():
    new_item = request.json
    if new_item and "name" in new_item:
        new_id = max([item["id"] for item in data["items"]]) + 1 if data["items"] else 1
        new_item["id"] = new_id
        data["items"].append(new_item)
        return jsonify(new_item), 201  # 201 Created
    return jsonify({"error": "Invalid item data"}), 400

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in data["items"] if item["id"] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)