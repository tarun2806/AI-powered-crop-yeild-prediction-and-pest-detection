import logging
import os

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLOps-Lite")

class MLOpsService:
    def __init__(self, baseline_data_path=None):
        logger.info("Initializing MLOps Lite (Vercel-Optimized)")
        
    def log_prediction(self, model_name, inputs, prediction, latency=None):
        """Logs prediction metadata to standard output (Mocking Prometheus for Vercel)."""
        logger.info(f"[MLOps-Mock][{model_name}] Prediction: {prediction} | Inputs: {inputs} | Simulation Latency: {latency}s")

    def detect_drift(self, model_name, current_data):
        """Mocked Drift Detection for Vercel-Lite."""
        return {"status": "Vercel-Lite: Simulation mode active. Real-time drift tracking disabled."}

# Singleton instance
mlops_service = MLOpsService()
