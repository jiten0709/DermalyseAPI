from flask import Blueprint, jsonify, request, current_app
from .models import Doctor, Patient, AnalysisResult
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
    print(f"Received data: {data}")  # Debug log

    if 'image' not in data or 'name' not in data or 'doctor_id' not in data:
        print("Missing required fields")  # Debug log
        return jsonify({'error': 'Missing required fields: image, name, or doctor_id'}), 400

    try:
        # Decode the Base64 string back into bytes
        image_bytes = base64.b64decode(data['image'])
        img = image.open(BytesIO(image_bytes))
        img = img.resize((299, 299))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
    except Exception as e:
        print(f"Invalid image data: {str(e)}")  # Debug log
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
    print(f"Top 3 predictions: {top3_predictions}")  # Debug log

    # Save the top prediction to the AnalysisResult table
    try:
        patient = Patient.query.filter_by(name=data['name']).first()
        if not patient:
            print("Patient not found")  # Debug log
            return jsonify({'error': 'Patient not found'}), 404

        analysis_result = AnalysisResult(
            patient_id=patient.id,
            doctor_id=data['doctor_id'],
            disease_name=list(top3_predictions.keys())[0],  # Top prediction
            disease_image=data['image'],  # Store Base64 image
            disease_score=list(top3_predictions.values())[0]  # Top prediction score
        )
        db.session.add(analysis_result)
        db.session.commit()
        print("Analysis result saved successfully")  # Debug log
    except Exception as e:
        db.session.rollback()
        print(f"Error saving analysis result: {str(e)}")  # Debug log
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
        # Check if the email is already registered
        existing_user = Doctor.query.filter_by(email=data["email"]).first() or Patient.query.filter_by(email=data["email"]).first()
        if existing_user:
            return jsonify({"error": "Email is already registered"}), 400

        if data["role"] == "Doctor":
            # Ensure specialization is provided for doctors
            specialization = data.get("specialization", "")
            if not specialization:
                return jsonify({"error": "Specialization is required for doctors"}), 400

            # Create a new doctor
            doctor = Doctor(
                name=data["name"],
                email=data["email"],
                password=data["password"],  # Include the password field
                specialization=specialization  # Use the provided specialization
            )
            db.session.add(doctor)
            db.session.commit()  # Commit to generate the ID
            return jsonify({
                "message": "Doctor registered successfully",
                "id": doctor.id,  # Return the ID of the newly created doctor
                "role": "Doctor"
            }), 201

        elif data["role"] == "Patient":
            # Create a new patient
            patient = Patient(
                name=data["name"],
                email=data["email"],
                password=data["password"],  # Include the password field
            )
            db.session.add(patient)
            db.session.commit()  # Commit to generate the ID
            return jsonify({
                "message": "Patient registered successfully",
                "id": patient.id,  # Return the ID of the newly created patient
                "role": "Patient"
            }), 201

        else:
            return jsonify({"error": "Invalid role"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")  # Expecting 'Doctor' or 'Patient'


    if not email or not password or not role:
        return jsonify({"error": "Missing email, password, or role"}), 400

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

    # Fetch all analysis results associated with the doctor
    analysis_results = AnalysisResult.query.filter_by(doctor_id=doctor_id).all()

    # Prepare the response with patient details and their latest analysis result
    response = []
    for result in analysis_results:
        patient = result.patient  # Access the patient via the relationship
        response.append({
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "latest_analysis": {
                "disease_name": result.disease_name,
                "disease_image": result.disease_image,
                "disease_score": result.disease_score,
                "timestamp": result.timestamp
            }
        })
    
    # print(f"Response: {response}")  # Debug log

    return jsonify(response), 200

@api_bp.route("/patients/<int:patient_id>/analysis", methods=["GET"])
def get_patient_analysis(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    analysis_results = AnalysisResult.query.filter_by(patient_id=patient_id).all()
    return jsonify([
        {
            "id": result.id,
            "disease_name": result.disease_name,
            "disease_image": result.disease_image,
            "disease_score": result.disease_score,
            "timestamp": result.timestamp
        }
        for result in analysis_results
    ])

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

@api_bp.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    return jsonify({
        "id": patient.id,
        "name": patient.name,
        "email": patient.email,
        "doctor_id": patient.doctor_id
    }), 200

@api_bp.route("/doctor/<int:doctor_id>/analysis", methods=["GET"])
def get_doctor_patient_analysis(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    analysis_results = AnalysisResult.query.filter_by(doctor_id=doctor_id).all()
    return jsonify([
        {
            "id": result.id,
            "patient_id": result.patient_id,
            "disease_name": result.disease_name,
            "disease_image": result.disease_image,
            "disease_score": result.disease_score,
            "timestamp": result.timestamp
        }
        for result in analysis_results
    ])
