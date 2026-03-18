# Master Architecture: AgroSaaS Agricultural Intelligence Platform

## 1. Executive Summary
The AgroSaaS platform is a high-performance, scalable ecosystem designed to provide farmers with data-driven insights. It has been transformed from a monolithic Python script into a distributed, production-grade SaaS architecture.

---

## 2. Platform Folder Structure (Production Layout)
```text
agro-saas/
├── flask_api/               # Core Backend Service
│   ├── app/                 # Application Logic
│   │   ├── api/             # Blueprints (Auth, Yield, Pest, IoT)
│   │   ├── models.py        # PostgreSQL SQLAlchemy Schemas
│   │   ├── schemas.py       # Marshmallow Validation
│   │   ├── services/        # Background Services (MQTT, Jobs)
│   │   ├── utils/           # MLOps, Weather API, Security
│   │   └── templates/       # V2 Modern Dashboard
│   ├── nginx/               # Reverse Proxy & SSL Config
│   ├── logs/                # Audit & MLOps Logs
│   └── run.py               # Main Entry Point
├── models/                  # AI Intelligence Layer
│   ├── train_*.py           # Advanced Training Pipelines
│   └── binary/              # .pkl and .h5 Production Weights
├── iot_layer/               # Hardware Firmware (ESP32/MQTT)
├── .github/workflows/       # CI/CD (Auto-deploy to AWS)
├── docker-compose.yml       # Stack Orchestration
└── SaaS_Cloud_Deployment.md # AWS Blueprint
```

---

## 3. High-Level Architecture Diagram
1.  **Ingress**: User (Browser/Mobile) -> **Nginx** (SSL/Proxy) -> **Gunicorn** (App Server).
2.  **App Tier**: **Flask REST API** handles JWT Auth, interacts with SQL, and triggers ML Inference.
3.  **Intelligence Tier**:
    *   **Yield Engine**: XGBoost Ensemble + Scikit-Learn.
    *   **CV Engine**: MobileNetV2 Transfer Learning (TensorFlow).
4.  **Hardware Tier**: **ESP32 Sensors** -> **Mosquitto MQTT** -> **Flask Subscriber**.
5.  **External Integ**: **OpenWeatherMap API** (merged with inference inputs).
6.  **Data Tier**: **PostgreSQL** (Managed via AWS RDS).

---

## 4. Key Performance Upgrades

### 🔒 Security & Auth
- **Stateless JWT**: All API requests are secured via JSON Web Tokens.
- **ORM abstraction**: Prevented SQL injection via SQLAlchemy.
- **Environment Secrets**: All keys (API, Database, JWT) are served via encrypted `.env` variables.

### 🧠 Model Intelligence
- **Drift Detection**: Uses Kolmogorov-Smirnov statistical tests to monitor data quality.
- **Transfer Learning**: Advanced pest detection using ImageNet-pretrained weights.
- **Latency Tracking**: Every inference is timed and logged for performance optimization.

### 🌊 Scalability
- **Containerization**: Fully Dockerized for "write once, run anywhere" consistency.
- **Horizontal Scaling**: Nginx upstream configuration allows adding multiple API containers easily.
- **IOT Gateway**: Handled via asynchronous MQTT listeners that don't block the main web thread.

---

## 5. Deployment & Roadmap

### Deployment Strategy
1. **Local**: `docker-compose up --build`
2. **Production**: GitHub Actions pushes to **Amazon ECR** -> Deployed to **Amazon EC2** -> **AWS RDS** database connectivity.

### Roadmap
- **Phase 1**: Edge Deployment (Exporting models to TFLite for offline mobile use).
- **Phase 2**: Geolocation sharding for large-scale sensor data.
- **Phase 3**: Integration with Satellite GIS data for soil health mapping.

---
*Redesigned by: Senior AI Architect*
