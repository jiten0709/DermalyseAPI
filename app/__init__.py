from flask import Flask
from .database import init_db
from .models import db
from flask_migrate import Migrate
from .routes import api_bp


def create_app():
    app = Flask(__name__)
    print("Initializing database...")
    init_db(app)  # Initialize the database
    print("Database initialized.")

    Migrate(app, db)
    
    app.register_blueprint(api_bp, url_prefix='/api')

    return app