from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image as image
from io import BytesIO
import base64
# from tensorflow.keras.preprocessing import image as keras_image


app = Flask(__name__)

# Load your model
model = tf.keras.models.load_model('new_xception_model.keras', compile=False)

class_labels = {
    'Acne': 0,
    'Actinic keratosis': 1,
    'Basal Cell Carcinoma': 2,
    'Benign Keratosis': 3,
    'Dermatofibroma': 4,
    'Eczema': 5,
    'Fungal Infection': 6,
    'Melanocytic Nevi': 7,
    'Melanoma': 8,
    'Rosacea': 9,
    'Squamous cell carcinoma': 10,
    'Urticaria Hives': 11,
    'Vascular Tumors': 12,
    'Viral Infections': 13,
    'Warts Molluscum': 14
}


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'hello'})


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'error': 'No image data'}), 400

    # Decode the Base64 string back into bytes
    image_bytes = base64.b64decode(data['image'])
    # Convert the bytes to a PIL Image object
    img = image.open(BytesIO(image_bytes))
    # Resize the image to the target size
    img = img.resize((299, 299))
    # Convert the image to a NumPy array
    img_array = tf.keras.preprocessing.image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0) / 255.

    # Assuming model is already loaded
    predictions = model.predict(img_array)
    instance_predictions = predictions[0]
    flattened_predictions = instance_predictions.flatten()
    sorted_indices = np.argsort(flattened_predictions)[::-1]

    # Initialize an empty list to store the sorted predictions
    sorted_predictions = []

    for index in sorted_indices:
        class_name = list(class_labels.keys())[index]
        # Convert float32 to float, multiply by 100 to get percentage, and round to 2 decimal places
        probability = round(float(flattened_predictions[index]) * 100, 2)
        # Store the class name and probability as a tuple
        if probability > 30:
            sorted_predictions.append((class_name, probability))
    
    # Convert the list of tuples into a dictionary
    top3_predictions = dict(sorted_predictions[:3])

    print(top3_predictions)

    return jsonify(top3_predictions)

@app.route('/test', methods=['GET'])
def test():
    # Open the image file
    with open('test_img.jpg', 'rb') as image_file:
        # Convert the file stream to bytes
        image_bytes = image_file.read()
    
    # Convert the bytes to a PIL Image object
    img = image.open(BytesIO(image_bytes))
    # Resize the image to the target size
    img = img.resize((299, 299))
    # Convert the image to a NumPy array
    img_array = tf.keras.preprocessing.image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0) / 255.

    # Assuming model is already loaded
    predictions = model.predict(img_array)
    instance_predictions = predictions[0]
    flattened_predictions = instance_predictions.flatten()
    sorted_indices = np.argsort(flattened_predictions)[::-1]

    # Initialize an empty list to store the sorted predictions
    sorted_predictions = []

    for index in sorted_indices:
        class_name = list(class_labels.keys())[index]
        # Convert float32 to float, multiply by 100 to get percentage, and round to 2 decimal places
        probability = round(float(flattened_predictions[index]) * 100, 2)
        # Store the class name and probability as a tuple
        if probability > 30:
            sorted_predictions.append((class_name, probability))
    
    # Convert the list of tuples into a dictionary
    top3_predictions = dict(sorted_predictions[:3])

    print(top3_predictions)

    return jsonify(top3_predictions)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
