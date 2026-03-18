from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, SensorData
from ..schemas import SensorDataSchema
from marshmallow import ValidationError

sensors_bp = Blueprint('sensors', __name__)
sensor_schema = SensorDataSchema()

@sensors_bp.route('/data', methods=['POST'])
@jwt_required()
def record_data():
    try:
        data = request.get_json()
        validated_data = sensor_schema.load(data)
        
        new_reading = SensorData(
            farm_id=validated_data.farm_id,
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            soil_moisture=data.get('soil_moisture'),
            ph_level=data.get('ph_level')
        )
        
        db.session.add(new_reading)
        db.session.commit()
        
        return jsonify({"message": "Sensor data recorded"}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
