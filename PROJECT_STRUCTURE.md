# 📂 AgroSaaS Project Structure Guide

This project is organized into three main modules: **Backend**, **AI**, and **IoT**.

---

## 🏗️ Root Directory
- `backend/`: The core Flask API and Dashboard.
- `iot/`: ESP32 firmware and hardware logic.
- `docs/`: Comprehensive documentation and architecture guides.
- `docker-compose.yml`: Orchestration for running the entire system.
- `prometheus.yml`: Monitoring configuration.
- `.env`: Environment variables (API keys, DB credentials).

---

## 🐍 Backend (`/backend`)
Think of this as the "Brain + Face" of the project. It handles the requests and shows the UI.

- `app/`:
    - `api/`: The logic for your features (Yield, Pest, Sensors).
    - `ai/`: **(Newly Optimized)** This folder now contains all ML model binaries (`.pkl`, `.h5`) and training scripts.
    - `templates/v2/`: Your modern Glassmorphism Dashboard (`dashboard.html`).
    - `utils/`: MLOps and Weather services.
    - `models.py`: Database table definitions.
- `run.py`: The main entry point. Run this to start the platform.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Container configuration for production.

---

## 🤖 AI Engine (`/backend/app/ai`)
This is where the intelligence lives.
- `pest_detection_model.h5`: The Deep Learning model for identifying pests.
- `crop_yield_pipeline.pkl`: The XGBoost model for yield forecasting.
- `train_*.py`: Scripts to retrain your models if you get new data.

---

## 🔌 Hardware IoT (`/iot`)
- `esp32/main.ino`: The firmware for your field sensors.

---

### **How to Run (Organized Method)**
1. **Virtual Env**: Use `source venv_agro/bin/activate`.
2. **Start Server**: 
   ```bash
   cd backend
   python run.py
   ```
3. **Access**: Open `http://localhost:5000` in your browser.
