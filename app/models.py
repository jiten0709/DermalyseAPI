from .database import db


class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email is required
    password = db.Column(db.String(255), nullable=False)  # Password is required
    specialization = db.Column(db.String(100), nullable=True)  # Specialization can be updated later

    # Relationship to link patients to a doctor
    patients = db.relationship('Patient', backref='doctor', lazy=True)

    def __repr__(self):
        return f"<Doctor {self.name}, Email: {self.email}, Specialization: {self.specialization}>"
    

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Foreign key to link the patient to a doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)

    # Relationship to link analysis results to a patient
    analysis_results = db.relationship('AnalysisResult', backref='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.name}, Email: {self.email}>"
    

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_result'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # Foreign key to Patient table
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)  # Optional: Doctor who performed the analysis
    disease_name = db.Column(db.String(100), nullable=False)  # Predicted disease
    disease_image = db.Column(db.Text, nullable=False)  # Base64-encoded image
    disease_score = db.Column(db.Float, nullable=False)  # Prediction confidence score
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Timestamp of the analysis

    def __repr__(self):
        return f"<AnalysisResult PatientID: {self.patient_id}, Disease: {self.disease_name}, Score: {self.disease_score}>"
    