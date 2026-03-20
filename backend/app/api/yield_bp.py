import os
import random
import time
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, PredictionHistory
from ..schemas import YieldPredictionSchema
from marshmallow import ValidationError
from ..utils.weather import weather_service

yield_bp = Blueprint('yield', __name__)
yield_schema = YieldPredictionSchema()
logger = logging.getLogger('Hybrid-Yield-AI')

# 🤖 Hybrid AI Inference Engine Setup
USE_MOCK = False
yield_model = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../ai/crop_yield_pipeline.pkl')

if os.environ.get('RENDER') == '1' or os.environ.get('VERCEL') == '1' or os.environ.get('USE_MOCK_AI') == '1':
    USE_MOCK = True
    logger.info("Environment set to RENDER/VERCEL. Forcing Mock Yield Prediction.")
else:
    try:
        import joblib
        import pandas as pd
        if not os.path.exists(MODEL_PATH):
            logger.warning("Yield Model not found locally. Falling back to Mock.")
            USE_MOCK = True
    except ImportError as e:
        logger.warning(f"ML packages not installed. Falling back to Mock AI. Reason: {e}")
        USE_MOCK = True

def get_yield_model():
    """Lazy load the harvest model to keep startup RAM low."""
    global yield_model
    if yield_model is None and not USE_MOCK:
        logger.info("Lazy Loading Scikit-Learn Yield Model...")
        import joblib
        yield_model = joblib.load(MODEL_PATH)
    return yield_model

@yield_bp.route('/predict', methods=['POST'])
def predict():
    try:
        validated_data = yield_schema.load(request.json)
        
        if USE_MOCK:
            # 🤖 CLOUD LITE MOCK ENGINE (Render Free Tier)
            base_yield = 2.5 # Average tons/hectare
            crop_multipliers = {
                "Rice": 1.2, "Wheat": 1.1, "Ragi": 0.8, "Maize": 1.4, "Sugarcane": 4.5
            }
            multiplier = crop_multipliers.get(validated_data.get('crop'), 1.0)
            random_factor = random.uniform(0.9, 1.1)
            prediction = float(validated_data.get('area', 1.0)) * base_yield * multiplier * random_factor
            mode_used = "Render-Lite Mock Simulation"
        else:
            # 🧠 LOCAL FULL ML MODEL ENGINE
            import pandas as pd
            input_df = pd.DataFrame([validated_data])
            # Drop target if accidentally included, rename columns to match model training if needed.
            # Assuming model takes the validated schema directly
            model = get_yield_model()
            prediction_array = model.predict(input_df)
            prediction = float(prediction_array[0])
            mode_used = "Local XGBoost/Scikit-Learn Model"
            
        # Save to history if logged in
        user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        if user_id:
            history = PredictionHistory(
                user_id=user_id,
                prediction_type='yield',
                inputs={"data": validated_data, "mode": mode_used},
                result=str(round(prediction, 2))
            )
            db.session.add(history)
            db.session.commit()

        return jsonify({
            "predicted_yield": round(prediction, 2),
            "unit": "tons per hectare",
            "system_status": mode_used
        }), 200
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        logger.error(f"Yield prediction error: {str(e)}")
        # Fail-safe degradation
        return jsonify({
            "predicted_yield": 3.14,
            "unit": "tons per hectare",
            "system_status": f"Fallback Mock due to error: {str(e)}"
        }), 200
