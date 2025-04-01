from flask import Blueprint, jsonify
from models.database import db

doctor_routes = Blueprint('doctor_routes', __name__)

@doctor_routes.route('/test_db', methods=['GET'])
def test_db():
    try:
        # Test query
        result = db.session.execute("SELECT * FROM user.doctor LIMIT 1;")
        doctors = [dict(row) for row in result]
        return jsonify({"success": True, "data": doctors})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    