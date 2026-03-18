# Upgrade Implementation Guide: Agricultural SaaS

## 1. REST API with JWT Authentication (FastAPI)
FastAPI is used for its automatic Swagger documentation and native async support.

```python
# api/app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "your-production-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_password_hash(password):
    return pwd_context.hash(password)
```

## 2. Advanced AI Engine (Yield & Pests)

### Yield Prediction: Model Comparison & Metrics
```python
# ml-engine/yield/trainers.py
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, r2_score, mean_absolute_error

def evaluate_models(X_train, X_test, y_train, y_test):
    models = {
        "XGBoost": xgb.XGBRegressor(n_estimators=500),
        "RandomForest": RandomForestRegressor(n_estimators=100)
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = {
            "R2": r2_score(y_test, preds),
            "MAE": mean_absolute_error(y_test, preds),
            "RMSE": root_mean_squared_error(y_test, preds)
        }
    return results
```

### Pest Detection: MobileNetV2 Transfer Learning
```python
# ml-engine/pest/transfer_learning.py
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D

def get_pest_model(num_classes):
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Freeze base model layers
    for layer in base_model.layers:
        layer.trainable = False
        
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', 'Precision', 'Recall'])
    return model
```

## 3. Real-time IoT via MQTT
```python
# iot-gateway/mqtt_client.py
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, message):
    data = json.loads(message.payload.decode("utf-8"))
    farm_id = message.topic.split('/')[1]
    # Save to PostgreSQL via SQLAlchemy session
    print(f"Recorded sensor data for Farm {farm_id}: {data}")

client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt.yourdomain.com", 1883)
client.subscribe("farm/+/sensors")
client.loop_forever()
```

## 4. Multilingual Strategy (Kannada Support)
Use **i18next** in the frontend and a JSON-based translation file.
```json
// locales/kn.json
{
    "DASHBOARD": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    "YIELD_PRED": "ಬೆಳೆ ಇಳುವರಿ ಮುನ್ಸೂಚನೆ",
    "PEST_DETECT": "ಕೀಟ ಪತ್ತೆ",
    "SOIL_MOISTURE": "ಮಣ್ಣಿನ ತೇವಾಂಶ"
}
```

## 5. Dockerization
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 6. Scaling & Security
1. **Vertical Scaling**: Use RDS Proxy for high-frequency sensor writes.
2. **Horizontal Scaling**: Kubernetes HPA (Horizontal Pod Autoscaler) based on CPU/RAM metrics.
3. **Security**: 
    - Use HTTPS everywhere.
    - Implement Rate Limiting on prediction endpoints to prevent cost spikes/DDoS.
    - Store all secrets in AWS Secrets Manager, never in `.env` files.
    - SQL Injection protection via SQLAlchemy ORM.

---
*Ready for Deployment.*
