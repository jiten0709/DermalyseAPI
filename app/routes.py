from flask import Blueprint, jsonify, request
from .models import db, Doctor, Patient
import tensorflow as tf
import numpy as np
from PIL import Image as image
from io import BytesIO
import base64

api_bp = Blueprint("api", __name__)


@api_bp.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'hello'})


# Load your model
model = tf.keras.models.load_model('assets/machineLearningModel/new_xception_model.keras', compile=False)

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

@api_bp.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if 'image' not in data or 'name' not in data or 'doctor_id' not in data:
        return jsonify({'error': 'Missing required fields: image, name, or doctor_id'}), 400

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

    # Save the top prediction to the database
    try:
        patient = Patient(
            name=data['name'],
            doctor_id=data['doctor_id'],
            disease_name=list(top3_predictions.keys())[0],  # Top prediction
            disease_image=data['image'],  # Store Base64 image
            disease_score=list(top3_predictions.values())[0]  # Top prediction score
        )
        db.session.add(patient)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify(top3_predictions)


@api_bp.route('/test', methods=['GET'])
def test():
    # Open the image file
    with open('assets/test-images/vascular.jpg', 'rb') as image_file:
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


@api_bp.route("/doctors", methods=["GET"])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([{"id": d.id, "name": d.name, "specialization": d.specialization} for d in doctors])

@api_bp.route("/doctor/<int:doctor_id>/patients", methods=["GET"])
def get_patients(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    patients = doctor.patients
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "disease_name": p.disease_name,
            "disease_image": p.disease_image,
            "disease_score": p.disease_score
        }
        for p in patients
    ])


@api_bp.route("/patients", methods=["POST"])
def add_patient():
    data = request.get_json()
    required_fields = ["name", "doctor_id", "disease_name", "disease_image", "disease_score"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        patient = Patient(
            name=data["name"],
            doctor_id=data["doctor_id"],
            disease_name=data["disease_name"],
            disease_image=data["disease_image"],
            disease_score=data["disease_score"]
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({"message": "Patient added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    