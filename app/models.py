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
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email is required
    password = db.Column(db.String(255), nullable=False)  # Password is required
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)  # Can be assigned later
    disease_name = db.Column(db.String(100), nullable=True)  # Can be updated later
    disease_image = db.Column(db.Text, nullable=True)  # Can be updated later
    disease_score = db.Column(db.Float, nullable=True)  # Can be updated later

    def __repr__(self):
        return f"<Patient {self.name}, Email: {self.email}, Disease: {self.disease_name}, Score: {self.disease_score}>"