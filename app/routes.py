from flask import Blueprint, jsonify, request, current_app
from .models import Doctor, Patient
from .database import db
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
model = tf.keras.models.load_model('app/assets/machineLearningModel/new_xception_model.keras', compile=False)

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

# IMAGE PREDICTION ENDPOINT
@api_bp.route("/doctors/predict", methods=["POST"])
def predict_for_doctor():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'error': 'Missing required field: image'}), 400

    try:
        # Decode the Base64 string back into bytes
        image_bytes = base64.b64decode(data['image'])
        img = image.open(BytesIO(image_bytes))
        img = img.resize((299, 299))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
    except Exception as e:
        return jsonify({'error': f'Invalid image data: {str(e)}'}), 400

    img_array = np.expand_dims(img_array, axis=0) / 255.

    # Predict using the model
    predictions = model.predict(img_array)
    instance_predictions = predictions[0]
    flattened_predictions = instance_predictions.flatten()
    sorted_indices = np.argsort(flattened_predictions)[::-1]

    sorted_predictions = []
    for index in sorted_indices:
        class_name = list(class_labels.keys())[index]
        probability = round(float(flattened_predictions[index]) * 100, 2)
        if probability > 30:
            sorted_predictions.append((class_name, probability))

    top3_predictions = dict(sorted_predictions[:3])

    # Return the predictions without storing them
    return jsonify(top3_predictions)

@api_bp.route("/patients/predict", methods=["POST"])
def predict_for_patient():
    data = request.get_json()
    if 'image' not in data or 'name' not in data or 'doctor_id' not in data:
        return jsonify({'error': 'Missing required fields: image, name, or doctor_id'}), 400

    try:
        # Decode the Base64 string back into bytes
        image_bytes = base64.b64decode(data['image'])
        img = image.open(BytesIO(image_bytes))
        img = img.resize((299, 299))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
    except Exception as e:
        return jsonify({'error': f'Invalid image data: {str(e)}'}), 400

    img_array = np.expand_dims(img_array, axis=0) / 255.

    # Predict using the model
    predictions = model.predict(img_array)
    instance_predictions = predictions[0]
    flattened_predictions = instance_predictions.flatten()
    sorted_indices = np.argsort(flattened_predictions)[::-1]

    sorted_predictions = []
    for index in sorted_indices:
        class_name = list(class_labels.keys())[index]
        probability = round(float(flattened_predictions[index]) * 100, 2)
        if probability > 30:
            sorted_predictions.append((class_name, probability))

    top3_predictions = dict(sorted_predictions[:3])

    # Save the top prediction to the database
    try:
        patient = Patient.query.filter_by(name=data['name']).first()
        if not patient:
            patient = Patient(
                name=data['name'],
                doctor_id=data['doctor_id'],
                disease_name=list(top3_predictions.keys())[0],  # Top prediction
                disease_image=data['image'],  # Store Base64 image
                disease_score=list(top3_predictions.values())[0]  # Top prediction score
            )
            db.session.add(patient)
        else:
            # Update existing patient record
            patient.disease_name = list(top3_predictions.keys())[0]
            patient.disease_image = data['image']
            patient.disease_score = list(top3_predictions.values())[0]

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify(top3_predictions)

# SIGNUP / SIGNIN ENDPOINT
@api_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    required_fields = ["name", "email", "password", "role"]  # Role: 'Doctor' or 'Patient'
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        if data["role"] == "Doctor":
            # Ensure specialization is provided for doctors
            specialization = data.get("specialization", "")
            if not specialization:
                return jsonify({"error": "Specialization is required for doctors"}), 400

            doctor = Doctor(
                name=data["name"],
                email=data["email"],
                password=data["password"],  # Include the password field
                specialization=specialization  # Use the provided specialization
            )
            db.session.add(doctor)
        elif data["role"] == "Patient":
            patient = Patient(
                name=data["name"],
                email=data["email"],
                password=data["password"],  # Include the password field
                doctor_id=None,  # Can be assigned later
                disease_name="",
                disease_image="",
                disease_score=0.0
            )
            db.session.add(patient)
        else:
            return jsonify({"error": "Invalid role"}), 400

        db.session.commit()
        return jsonify({"message": f"{data['role']} registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")  # Expecting 'Doctor' or 'Patient'

    if role == "Doctor":
        # Check if the user is a doctor
        doctor = Doctor.query.filter_by(email=email, password=password).first()
        if doctor:
            return jsonify({
                "id": doctor.id,
                "role": "Doctor",
                "name": doctor.name,
                "email": doctor.email,
                "specialization": doctor.specialization
            }), 200

    elif role == "Patient":
        # Check if the user is a patient
        patient = Patient.query.filter_by(email=email, password=password).first()
        if patient:
            return jsonify({
                "id": patient.id,
                "role": "Patient",
                "name": patient.name,
                "email": patient.email,
                "doctor_id": patient.doctor_id,
                "disease_name": patient.disease_name,
                "disease_score": patient.disease_score
            }), 200

    return jsonify({"error": "Invalid email, password, or role"}), 401

# DOCTOR ENDPOINTS

@api_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    return jsonify({
        "id": doctor.id,
        "name": doctor.name,
        "email": doctor.email,
        "specialization": doctor.specialization
    }), 200

@api_bp.route("/doctors", methods=["GET"])
def get_doctors():
    doctors = Doctor.query.limit(10).all()  # Limit the query to 10 doctors
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

@api_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    data = request.get_json()
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    try:
        if "specialization" in data:
            doctor.specialization = data["specialization"]

        db.session.commit()
        return jsonify({"message": "Doctor details updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# PATIENT ENDPOINTS
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

@api_bp.route("/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.get_json()
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    try:
        if "doctor_id" in data:
            patient.doctor_id = data["doctor_id"]
        if "disease_name" in data:
            patient.disease_name = data["disease_name"]
        if "disease_image" in data:
            patient.disease_image = data["disease_image"]
        if "disease_score" in data:
            patient.disease_score = data["disease_score"]

        db.session.commit()
        return jsonify({"message": "Patient details updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route("/patients", methods=["GET"])
def get_all_patients():
    patients = Patient.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "doctor_id": p.doctor_id,
            "disease_name": p.disease_name,
            "disease_image": p.disease_image,
            "disease_score": p.disease_score
        }
        for p in patients
    ])