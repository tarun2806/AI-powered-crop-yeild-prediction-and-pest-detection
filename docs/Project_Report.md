# Project Report: AI-Powered Crop Yield Prediction and Pest Detection

## 1. Project Overview
This project is an AI-driven agricultural management system designed to help farmers optimize their crop yields and manage pests effectively. It combines machine learning models with real-time sensor data to provide actionable insights.

## 2. Core Modules

### 2.1 Crop Yield Prediction
- **Technology**: Built using a **Random Forest Regressor** (Scikit-Learn).
- **Functionality**: Predicts the expected harvest volume (tons per hectare) based on multiple factors:
    - **Regional Data**: Specifically tuned for districts in Karnataka.
    - **User Inputs**: Crop type (Rice, Wheat, Ragi, etc.), Area, and Soil type.
    - **Environmental Data**: Integrates temperature, humidity, and soil moisture.
- **Training**: Trained on a dataset that models regional agricultural patterns, ensuring relevance to local farming conditions.

### 2.2 Pest Detection & Management
- **Technology**: Implements a **Convolutional Neural Network (CNN)** (TensorFlow/Keras).
- **Image Recognition**: Users can upload photos of crops to identify pests.
- **Supported Pests**:
    - Aphids
    - Stem Borers
    - Cutworms
    - Thrips
    - Armyworms
- **Actionable Advice**: Once a pest is identified, the system provides specific **fertilizer recommendations** to mitigate the infestation and improve plant health.

### 2.3 Sensor Integration
- **Status**: Ready for real-time hardware integration.
- **Sensors**: Designed to interface with Arduino sensors for:
    - Temperature
    - Humidity
    - Soil Moisture
    - pH Levels
- **Implementation**: Currently uses a simulation module (`sensors/arduino_data.py`) which can be easily swapped for actual serial data from an Arduino board.

## 3. Technical Architecture

### 3.1 Backend Stack
- **Framework**: Flask (Python)
- **Data Processing**: Pandas, NumPy
- **Model Storage**: Joblib (for Random Forest), H5 (for CNN)

### 3.2 Frontend Stack
- **Languages**: HTML5, CSS3, JavaScript
- **Features**: Responsive design, multilingual support framework, and asynchronous model inference (AJAX).

### 3.3 Folder Structure
- `app.py`: The central hub handling requests and model inference.
- `models/`: Contains the `.pkl` and `.h5` model files plus the `train_*.py` scripts for future retraining.
- `sensors/`: Logic for hardware data acquisition.
- `templates/`: HTML views for Dashboard, Yield Prediction, and Pest Detection.
- `static/`: CSS, JavaScript, and asset files.

## 4. Key Strengths
- **Localized Design**: Focuses on Karnataka's geography and crops.
- **Dual AI Power**: Combines tabular data prediction (Yield) with computer vision (Pests).
- **User-Centric**: Provides not just detection but also solutions (fertilizer advice).
- **Scalable**: The modular architecture allows for adding more crops, districts, and pest types easily.

## 5. Potential Future Enhancements
- **Live IoT Integration**: Connect actual Arduino/ESP32 sensors for live field monitoring.
- **Weather API**: Integrate real-time weather forecasts to replace or supplement sensor data.
- **Disease Detection**: Expand the CNN model to detect plant diseases beyond just pests.
- **Mobile App**: Port the interface to a mobile application for easier field use.

---
*Report Generated: February 19, 2024*
*Third Year Mini Project Analysis*
