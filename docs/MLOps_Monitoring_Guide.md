# MLOps Monitoring & Drift Detection Guide

This platform uses professional MLOps practices to ensure your AI models stay accurate and reliable over time.

## 1. Real-time Monitoring
We use **Prometheus** to track live model performance metrics. 
- **Endpoint**: `/metrics`
- **Key Metrics**:
    - `ml_predictions_total`: Tracks the volume of predictions per model.
    - `ml_prediction_latency_seconds`: Monitors the time it takes for a model to run an inference (CNNs take longer than RF).
    - `ml_model_drift_score`: Real-time statistical drift score for every input feature.

## 2. Model Drift Detection
Model drift occurs when the data your model sees in the field (e.g., modern climate) differs from the data it was trained on (baseline).

### How it Works:
- **Baseline Analysis**: We compare current incoming request data against a "Golden Dataset" from training.
- **Statistical Test**: We use the **Kolmogorov-Smirnov (KS) Test**.
- **Alerting**: 
    - If the p-value drops below **0.05**, the distributions are statistically different.
    - The system logs an `🚨 [DRIFT DETECTED]` error immediately.
    - This score is exposed to Prometheus, allowing for automatic Slack/Email alerts via PagerDuty or Grafana.

## 3. Logging & Auditing
Every prediction is logged in `logs/agro_api.log` with:
- Model Name
- Input Parameters (Merged with live weather)
- Prediction Result
- Execution Latency

## 4. Scaling the Monitoring Stack
To visualize these metrics at scale:
1. **Prometheus Server**: Scrape the `/metrics` endpoint every 15 seconds.
2. **Grafana Dashboard**: Create a "Model Health" dashboard.
3. **Drift Remediation**: Once drift is detected, use the **CI/CD pipeline** to retrain the model on the latest data and redeploy automatically.

---
*Maintained by: MLOps Engineering Team*
