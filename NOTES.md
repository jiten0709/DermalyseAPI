CREATE TABLE user.doctor (
doctor_id SERIAL PRIMARY KEY,
doctor_name VARCHAR(100) NOT NULL
);

CREATE TABLE user.patient (
patient_id SERIAL PRIMARY KEY,
patient_name VARCHAR(100) NOT NULL,
patient_image TEXT,
disease_name VARCHAR(100),
disease_probability FLOAT,
doctor_id INT REFERENCES user.doctor(doctor_id)
);
