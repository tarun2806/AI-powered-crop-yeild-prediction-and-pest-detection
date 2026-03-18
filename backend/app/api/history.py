from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import PredictionHistory

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = PredictionHistory.query.filter_by(user_id=user_id).order_by(PredictionHistory.created_at.desc()).all()
    
    results = []
    for record in history:
        results.append({
            "id": str(record.id),
            "type": record.prediction_type,
            "inputs": record.inputs,
            "result": record.result,
            "confidence": record.confidence,
            "created_at": record.created_at.isoformat()
        })
        
    return jsonify(results), 200
