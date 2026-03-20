import os
import random
import time
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, PredictionHistory

pest_bp = Blueprint('pest', __name__)
logger = logging.getLogger('Hybrid-Pest-AI')

# 🤖 Hybrid AI Inference Engine Setup
USE_MOCK = False
tf_model = None

# Check if we are forced into mock mode by Environment (Render/Vercel)
if os.environ.get('RENDER') == '1' or os.environ.get('VERCEL') == '1' or os.environ.get('USE_MOCK_AI') == '1':
    USE_MOCK = True
    logger.info("Environment set to RENDER/VERCEL. Forcing Mock Pest Inference.")
else:
    try:
        import tensorflow as tf
        import numpy as np
        from PIL import Image
        import io
        MODEL_PATH = os.path.join(os.path.dirname(__file__), '../ai/pest_detection_model.h5')
        if not os.path.exists(MODEL_PATH):
            logger.warning("TensorFlow Model not found locally. Falling back to Mock.")
            USE_MOCK = True
    except ImportError as e:
        logger.warning(f"TensorFlow not installed. Falling back to Mock AI. Reason: {e}")
        USE_MOCK = True

def get_tf_model():
    """Lazy load the massive AI model only when needed to prevent huge startup RAM usage!"""
    global tf_model
    if tf_model is None and not USE_MOCK:
        logger.info("Lazy Loading TensorFlow Pest Detection Model...")
        tf_model = tf.keras.models.load_model(MODEL_PATH)
    return tf_model

CLASSES = ["Aphids", "Stem Borers", "Cutworms", "Thrips", "Armyworms"]

classes_info = {
    "Aphids": {
        "threat": "High",
        "treatment": "Spray neem oil or insecticidal soap. Introduce natural predators like ladybugs.",
        "prevention": "Avoid over-fertilizing with nitrogen, which attracts aphids."
    },
    "Stem Borers": {
        "threat": "Critical",
        "treatment": "Remove and destroy infested plants. Use Bacillus thuringiensis (Bt) or carbaryl-based sprays.",
        "prevention": "Crop rotation and intercropping with non-host plants."
    },
    "Cutworms": {
        "threat": "Medium",
        "treatment": "Hand-pick at night. Apply diatomaceous earth around the base of plants.",
        "prevention": "Keep the garden clean of debris where larvae might hide."
    },
    "Thrips": {
        "threat": "Low-Medium",
        "treatment": "Use blue or yellow sticky traps. Spray water to knock them off leaves.",
        "prevention": "Maintain adequate irrigation to reduce stress on plants."
    },
    "Armyworms": {
        "threat": "Critical",
        "treatment": "Apply Spinosad or Bt-based insecticides. Hand-removal for small infestations.",
        "prevention": "Monitor light traps to detect adult moth activity early."
    }
}

@pest_bp.route('/detect', methods=['POST'])
def detect():
    try:
        if USE_MOCK:
            # 🤖 CLOUD LITE MOCK ENGINE (Render Free Tier)
            result = random.choice(CLASSES)
            confidence = round(random.uniform(0.88, 0.98), 4)
            mode_used = "Render-Lite Mock Simulation"
            time.sleep(0.5) # Simulate inference time
        else:
            # 🧠 LOCAL FULL TENSORFLOW ENGINE
            if 'image' not in request.files:
                return jsonify({"error": "No image provided for real inference"}), 400
            file = request.files['image']
            img = Image.open(file.stream).convert('RGB')
            img = img.resize((224, 224)) # Assuming MobileNetV2 input shape
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            model = get_tf_model()
            predictions = model.predict(img_array)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(np.max(predictions[0]))
            
            # Map index to class
            result = CLASSES[predicted_class_idx % len(CLASSES)]
            mode_used = "Local TensorFlow CNN (MobileNetV2)"

        pest_info = classes_info.get(result, classes_info["Aphids"])
        
        # Save to DB if logged in
        user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        if user_id:
            history = PredictionHistory(
                user_id=user_id,
                prediction_type='pest',
                inputs={"mode": mode_used, "file_uploaded": bool(request.files.get('image'))},
                result=result,
                confidence=confidence
            )
            db.session.add(history)
            db.session.commit()

        return jsonify({
            "pest": result,
            "confidence": confidence,
            "threat_level": pest_info["threat"],
            "treatment": pest_info["treatment"],
            "prevention": pest_info["prevention"],
            "system_status": mode_used
        }), 200

    except Exception as e:
        logger.error(f"Pest detection error: {str(e)}")
        # Fail-safe mechanism: degrade to mock on failure
        result = random.choice(CLASSES)
        pest_info = classes_info.get(result)
        return jsonify({
            "pest": result,
            "confidence": 0.85,
            "threat_level": pest_info["threat"],
            "treatment": pest_info["treatment"],
            "prevention": pest_info["prevention"],
            "system_status": f"Fallback Mock due to error: {str(e)}"
        }), 200

@pest_bp.route('/recommendation', methods=['GET'])
def get_recommendation():
    """Returns general pest control recommendations based on crop and current weather."""
    crop = request.args.get('crop', 'Rice')
    
    # Simple rule-based engine for high-density agriculture
    recommendations = {
        "Rice": {
            "pests": ["Stem Borers", "Aphids"],
            "prevention": "Ensure proper drainage and avoid flooding for too long.",
            "emergency_contact": "Regional Agri-Helpline: 1800-XXX-XXXX"
        },
        "Wheat": {
            "pests": ["Rusts", "Aphids"],
            "prevention": "Use resistant varieties and monitor moisture levels.",
            "emergency_contact": "Wheat Disease Hotline: 1800-YYY-YYYY"
        },
        "Maize": {
            "pests": ["Fall Armyworm", "Corn Borer"],
            "prevention": "Intercrop with legumes to reduce pest pressure.",
            "emergency_contact": "Maize Council Help desk: 1800-ZZZ-ZZZZ"
        }
    }
    
    data = recommendations.get(crop, recommendations["Rice"])
    
    return jsonify({
        "crop": crop,
        "recommendations": data,
        "status": "ok"
    }), 200
