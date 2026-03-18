import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from prometheus_client import Gauge, Counter, Summary
import logging
import os

# Prometheus Metrics
PREDICTION_COUNT = Counter('ml_predictions_total', 'Total number of ML predictions', ['model_name'])
MODEL_DRIFT_SCORE = Gauge('ml_model_drift_score', 'Model drift score (p-value of KS test)', ['model_name', 'feature_name'])
PREDICTION_LATENCY = Summary('ml_prediction_latency_seconds', 'Latency of ML predictions in seconds', ['model_name'])

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLOps")

class MLOpsService:
    def __init__(self, baseline_data_path=None):
        self.baseline_data = None
        if baseline_data_path and os.path.exists(baseline_data_path):
            self.baseline_data = pd.read_csv(baseline_data_path)
            logger.info(f"Loaded baseline data from {baseline_data_path}")
        
    def log_prediction(self, model_name, inputs, prediction, latency=None):
        """Logs prediction metadata and updates Prometheus metrics."""
        PREDICTION_COUNT.labels(model_name=model_name).inc()
        if latency:
            PREDICTION_LATENCY.labels(model_name=model_name).observe(latency)
        
        logger.info(f"[{model_name}] Prediction: {prediction} | Inputs: {inputs}")

    def detect_drift(self, model_name, current_data: pd.DataFrame):
        """
        Detects feature drift by comparing current data to baseline using the Kolmogorov-Smirnov test.
        Returns a dictionary of drift status per feature.
        """
        if self.baseline_data is None:
            logger.warning("No baseline data available for drift detection.")
            return {}

        drift_results = {}
        for feature in self.baseline_data.columns:
            if feature in current_data.columns and np.issubdtype(self.baseline_data[feature].dtype, np.number):
                # Kolmogorov-Smirnov test
                stat, p_value = ks_2samp(self.baseline_data[feature], current_data[feature])
                MODEL_DRIFT_SCORE.labels(model_name=model_name, feature_name=feature).set(p_value)
                
                # If p-value < 0.05, distributions are statistically different (Drift detected)
                is_drifting = p_value < 0.05
                drift_results[feature] = {
                    "p_value": round(p_value, 4),
                    "is_drifting": is_drifting
                }
                
                if is_drifting:
                    logger.error(f"🚨 [DRIFT DETECTED] Feature '{feature}' in model '{model_name}' (p-value: {p_value:.4f})")
        
        return drift_results

# Singleton instance
# Ideally, we'd pass a real baseline dataset here
mlops_service = MLOpsService()
