from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    # Relationship to link patients to a doctor
    patients = db.relationship('Patient', backref='doctor', lazy=True)

    def __repr__(self):
        return f"<Doctor {self.name}, Specialization: {self.specialization}>"

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False) 
    disease_name = db.Column(db.String(100), nullable=False)
    disease_image = db.Column(db.Text, nullable=False)  # Store Base64 or file path
    disease_score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Patient {self.name}, Disease: {self.disease_name}, Score: {self.disease_score}>"