from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from .config import Config

db = SQLAlchemy()

def init_db(app: Flask):
    """Initialize the database with the Flask app."""
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist

    return db
