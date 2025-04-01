from flask import Flask
from .database import init_db
from .models import db

def create_app():
    app = Flask(__name__)
    init_db(app)  # Initialize the database
    
    from .routes import api_bp
    app.register_blueprint(api_bp)

    return app
