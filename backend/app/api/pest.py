from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import time
from ..models import db, PredictionHistory
from ..utils.mlops import mlops_service


pest_bp = Blueprint('pest', __name__)

# Load model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai', 'pest_detection_model.h5')
model = tf.keras.models.load_model(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
CLASSES = ["Aphids", "Stem Borers", "Cutworms", "Thrips", "Armyworms"]

@pest_bp.route('/detect', methods=['POST'])
def detect():
    if not model:
        return jsonify({"error": "Model not found"}), 500
        
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    try:
        start_time = time.time()
        image = Image.open(io.BytesIO(file.read())).convert('RGB')
        image = image.resize((128, 128))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array)
        latency = time.time() - start_time
        class_idx = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))
        result = CLASSES[class_idx]
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

        pest_info = classes_info.get(result, {
            "threat": "Unknown",
            "treatment": "Consult a local agricultural expert.",
            "prevention": "Monitor crop health regularly."
        })

        # Save to history if logged in
        user_id = get_jwt_identity()
        if user_id:
            history = PredictionHistory(
                user_id=user_id,
                prediction_type='pest',
                inputs={"filename": file.filename},
                result=result,
                confidence=confidence
            )
            db.session.add(history)
            db.session.commit()
        
        return jsonify({
            "pest": result,
            "confidence": round(confidence, 4),
            "threat_level": pest_info["threat"],
            "treatment": pest_info["treatment"],
            "prevention": pest_info["prevention"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
