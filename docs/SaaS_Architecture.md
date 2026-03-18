# Production-Grade AI Agricultural SaaS Architecture

## 1. System Overview
Transforming a monolithic Flask app into a distributed, scalable SaaS platform using a Microservices-inspired architecture.

### Tech Stack
- **Backend**: FastAPI (Python) - *Chosen over Flask for native async support, pydantic validation, and faster execution.*
- **Database**: PostgreSQL (Relational) + Redis (Caching & Task Queue)
- **Auth**: OAuth2 with JWT (JSON Web Tokens)
- **AI/ML**: 
    - **Yield**: XGBoost & Random Forest (Ensemble)
    - **Pests**: MobileNetV2 (Transfer Learning)
- **IoT**: MQTT (using EMQX or Mosquitto)
- **DevOps**: Docker, Kubernetes (EKS), Terraform
- **Monitoring**: Prometheus, Grafana, ELK Stack

---

## 2. Platform Folder Structure (Modern Layout)

```text
agro-saas/
├── api/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API Routes (v1)
│   │   ├── core/           # Security, Config, JWT
│   │   ├── db/             # Base, Sessions, Migrations
│   │   ├── models/         # SQLAlchemy Schemas
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── services/       # Business Logic (Calculations, IoT)
│   │   └── main.py
│   ├── docker/
│   └── requirements.txt
├── ml-engine/              # Model Training & Inference
│   ├── yield/
│   │   ├── trainers/       # XGBoost/RF Runners
│   │   └── evaluator.py
│   ├── pest/
│   │   ├── transfer_learning.py (MobileNetV2)
│   │   └── processor.py
│   └── drift_detector.py
├── iot-gateway/            # MQTT Broker Integration
│   ├── mqtt_client.py
│   └── processor.py
├── scripts/                # Database seeders, migrations
├── docker-compose.yml
└── .env
```

---

## 3. Database Schema (PostgreSQL)

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'farmer', -- farmer, analyst, admin
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Farms Table
```sql
CREATE TABLE farms (
    id UUID PRIMARY KEY,
    owner_id UUID REFERENCES users(id),
    name VARCHAR(255),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    total_area FLOAT,
    soil_type VARCHAR(100)
);
```

### Crop Records & History
```sql
CREATE TABLE crops (
    id UUID PRIMARY KEY,
    farm_id UUID REFERENCES farms(id),
    crop_name VARCHAR(100),
    planting_date DATE,
    status VARCHAR(50) -- 'growing', 'harvested'
);

CREATE TABLE predictions (
    id UUID PRIMARY KEY,
    farm_id UUID REFERENCES farms(id),
    type VARCHAR(20), -- 'yield' or 'pest'
    input_data JSONB,
    result FLOAT, -- yield value or pest_id
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### IoT Sensor Logs (Time-Series)
*Ideally used with TimescaleDB plugin for Postgres.*
```sql
CREATE TABLE sensor_logs (
    time TIMESTAMP NOT NULL,
    farm_id UUID REFERENCES farms(id),
    temperature FLOAT,
    humidity FLOAT,
    soil_moisture FLOAT,
    ph_level FLOAT
);
SELECT create_hypertable('sensor_logs', 'time');
```

---

## 4. API Design (RESTful)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/auth/register` | POST | Register new farmer |
| `/auth/login` | POST | Get JWT token |
| `/farms` | GET/POST | List/Create farm locations |
| `/predict/yield` | POST | Multi-model yield inference |
| `/predict/pest` | POST | Image upload for CNN detection |
| `/sensors/live` | GET | Real-time stream (Websockets) |
| `/history` | GET | Past predictions and crop cycles |

---

## 5. AI Upgrade Strategy

### Transfer Learning for Pest Detection
Utilizing **MobileNetV2** for mobile-friendly, high-accuracy inference.
```python
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D

def build_transfer_model(num_classes):
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False  # Freeze initial layers
    
    model = tf.keras.Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(512, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    return model
```

### Yield Prediction: XGBoost Implementation
```python
import xgboost as xgb
from sklearn.metrics import r2_score, mean_absolute_error

def train_yield_xgboost(X_train, y_train):
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8
    )
    model.fit(X_train, y_train)
    return model
```

---

## 6. Real-time IoT (MQTT Workflow)
1. **Physical Layer**: Arduino with ESP8266/ESP32 publishes data to `farm/{id}/sensors`.
2. **Broker**: EMQX or AWS IoT Core receives the payload.
3. **Consumer**: A dedicated service (Python/Node) listens to the MQTT topic.
4. **Processing**: Validates data and persists to PostgreSQL.
5. **Real-time UI**: Backend broadcasts via **WebSockets** for live dashboard updates.

---

## 7. AWS Cloud Architecture
- **Inbound**: CloudFront (CDN) -> S3 (Static Frontend) -> ALB (Application Load Balancer)
- **Compute**: AWS EKS (Kubernetes) for Autoscaling Backend nodes.
- **Storage**: Amazon RDS (PostgreSQL) + Amazon Elasticache (Redis).
- **ML**: SageMaker for periodic retraining and drift detection.
- **Security**: AWS WAF (Firewall) + IAM (Role-based access).

---

## 8. Future Roadmap & Scaling
- **Phase 1**: Vertical scaling (High-RAM RDS instances).
- **Phase 2**: Geolocation-based Sharding for the sensor data.
- **Phase 3**: Edge AI (Running the Pest Detection model directly on a mobile app using TFLite to save server bandwidth).
- **Phase 4**: Satellite Imagery integration for large-scale yield monitoring.

---
*Architected by: Senior AI Architect*
