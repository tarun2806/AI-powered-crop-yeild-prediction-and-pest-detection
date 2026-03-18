# AgroSaaS | AI-Powered Agricultural Intelligence

A production-ready SaaS platform for crop yield prediction, pest detection, and real-time sensor monitoring.

## 📂 Project Structure

- **`backend/`**: The core SaaS engine.
  - `app/api/`: REST endpoints (Auth, Predictions, IoT).
  - `app/ai/`: Model weights and training scripts.
  - `app/templates/v2/`: Modern Glassmorphism Dashboard UI.
- **`iot/`**: ESP32 C++ firmware for field sensor integration.
- **`docs/`**: Comprehensive architecture and MLOps deployment guides.

## 🚀 Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **Run the Platform**:
   ```bash
   cd backend
   python run.py
   ```

Visit `http://localhost:5000` to access the dashboard.

## 🌦️ Key Features
- **Weather Integration**: Automatically merges live data from OpenWeatherMap.
- **MLOps**: Built-in Kolmogorov-Smirnov drift detection and Prometheus monitoring.
- **IoT Resilience**: MQTT-based sensor handling with offline recovery.
- **Bi-Lingual**: English and Kannada (ಕನ್ನಡ) language support.

---
*Built for Scalability. Architected for Impact.*
