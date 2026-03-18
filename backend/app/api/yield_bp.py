from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import joblib
import pandas as pd
import os
import time
from ..models import db, PredictionHistory
from ..schemas import YieldPredictionSchema
from marshmallow import ValidationError
from ..utils.weather import weather_service
from ..utils.mlops import mlops_service



yield_bp = Blueprint('yield', __name__)
yield_schema = YieldPredictionSchema()

# Load model (Adjust path as needed)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai', 'crop_yield_pipeline.pkl')
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

@yield_bp.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not found"}), 500
        
    try:
        # Load and validate data
        validated_data = yield_schema.load(request.json)
        
        # 🌦️ Fetch and Merge Real-time Weather Data
        weather = weather_service.get_weather(validated_data['district'])
        if weather:
            # Only update if not explicitly provided or if provided as 0
            if not validated_data.get('temperature'):
                validated_data['temperature'] = weather['temperature']
            if not validated_data.get('humidity'):
                validated_data['humidity'] = weather['humidity']
            # You can add more fields like rainfall if your model uses it

        # Prepare data for prediction
        input_df = pd.DataFrame([validated_data])
        input_encoded = pd.get_dummies(input_df)

        start_time = time.time()
        
        # Align features
        for col in model.feature_names_in_:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        input_encoded = input_encoded[model.feature_names_in_]
        
        prediction = model.predict(input_encoded)[0]
        latency = time.time() - start_time

        # 📊 MLOps Logging
        mlops_service.log_prediction(
            model_name="yield_rf", 
            inputs=validated_data, 
            prediction=round(prediction, 2),
            latency=latency
        )

        
        # Save to history if logged in
        user_id = get_jwt_identity()
        if user_id:
            history = PredictionHistory(
                user_id=user_id,
                prediction_type='yield',
                inputs=validated_data,
                result=str(round(prediction, 2))
            )
            db.session.add(history)
            db.session.commit()
        
        return jsonify({
            "predicted_yield": round(prediction, 2),
            "unit": "tons per hectare"
        }), 200
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
