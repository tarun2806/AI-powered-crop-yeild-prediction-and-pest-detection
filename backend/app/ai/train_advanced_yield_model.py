import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Seed for reproducibility
np.random.seed(42)

class CropYieldEngine:
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        self.best_model = None
        self.feature_names = None
        self.categorical_mappings = {}

    def generate_data(self, samples=2000):
        """Generates realistic synthetic data for Karnataka districts."""
        districts = ['Bagalkot', 'Ballari', 'Belagavi', 'Bengaluru', 'Bidar', 'Chamarajanagar', 'Mysuru', 'Tumakuru']
        crops = ['Wheat', 'Rice', 'Ragi', 'Jower', 'Sugarcane', 'Coffee', 'Cotton']
        soil_types = ['Clay', 'Red', 'Black', 'Alluvial']

        data = pd.DataFrame({
            'district': np.random.choice(districts, samples),
            'area': np.random.uniform(1, 100, samples),
            'crop': np.random.choice(crops, samples),
            'soil_type': np.random.choice(soil_types, samples),
            'temperature': np.random.uniform(18, 42, samples),
            'humidity': np.random.uniform(20, 95, samples),
            'rainfall': np.random.uniform(400, 3000, samples),
            'soil_moisture': np.random.uniform(5, 70, samples),
        })

        # Create a more realistic target variable
        # Yield depends on area, temperature (sweet spot 25-30), and crop type
        base_yield = (data['area'] * 0.05) + (data['soil_moisture'] * 0.02)
        temp_effect = -0.01 * (data['temperature'] - 27)**2 + 1
        data['yield'] = (base_yield * temp_effect) + np.random.normal(0, 0.5, samples)
        data['yield'] = data['yield'].clip(lower=0.5)

        return data

    def preprocess(self, data):
        """One-hot encodes and saves feature structure."""
        data_encoded = pd.get_dummies(data, columns=['district', 'crop', 'soil_type'])
        X = data_encoded.drop('yield', axis=1)
        y = data_encoded['yield']
        self.feature_names = X.columns.tolist()
        return X, y

    def train_and_evaluate(self, X, y):
        """Trains RF and XGBoost, performs K-Fold CV, and selects best model."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
            "XGBoost": xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
        }

        best_score = -np.inf
        results = {}

        for name, model in models.items():
            print(f"\n--- Evaluating {name} ---")
            
            # K-Fold Cross Validation
            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, X, y, cv=kf, scoring='r2')
            print(f"CV R2 Scores: {cv_scores}")
            print(f"Mean CV R2: {cv_scores.mean():.4f}")

            # Fit and Test
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
            r2 = r2_score(y_test, preds)
            mae = mean_absolute_error(y_test, preds)
            rmse = root_mean_squared_error(y_test, preds)

            print(f"Test R2: {r2:.4f}")
            print(f"Test MAE: {mae:.4f}")
            print(f"Test RMSE: {rmse:.4f}")

            results[name] = {"r2": r2, "model": model}

            if r2 > best_score:
                best_score = r2
                self.best_model = model
                self.best_model_name = name

        print(f"\n🏆 Best Model: {self.best_model_name} (R2: {best_score:.4f})")
        return results

    def plot_importance(self):
        """Visualizes feature importance of the best model."""
        if hasattr(self.best_model, 'feature_importances_'):
            importances = self.best_model.feature_importances_
            indices = np.argsort(importances)[-10:] # Top 10
            
            plt.figure(figsize=(10, 6))
            plt.title(f'Top 10 Feature Importances ({self.best_model_name})')
            plt.barh(range(len(indices)), importances[indices], align='center')
            plt.yticks(range(len(indices)), [self.feature_names[i] for i in indices])
            plt.xlabel('Relative Importance')
            plt.tight_layout()
            plt.savefig(os.path.join(self.model_dir, 'feature_importance.png'))
            print(f"Importance plot saved to {self.model_dir}/feature_importance.png")

    def save_pipeline(self):
        """Saves model and metadata for production."""
        metadata = {
            "model": self.best_model,
            "features": self.feature_names,
            "model_name": self.best_model_name
        }
        joblib.dump(metadata, os.path.join(self.model_dir, "crop_yield_pipeline.pkl"))
        print(f"Production pipeline saved to {self.model_dir}/crop_yield_pipeline.pkl")

# --- Production Wrapper ---
def predict_yield(input_dict):
    """
    Wrapper for production inference.
    Input format: {'district': 'Mysuru', 'area': 10, 'crop': 'Rice', ...}
    """
    pipeline = joblib.load("models/crop_yield_pipeline.pkl")
    model = pipeline["model"]
    features = pipeline["features"]
    
    # Convert input to DataFrame
    df = pd.DataFrame([input_dict])
    df_encoded = pd.get_dummies(df)
    
    # Align with training features
    for col in features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_final = df_encoded[features]
    
    prediction = model.predict(df_final)[0]
    return round(float(prediction), 2)

if __name__ == "__main__":
    engine = CropYieldEngine()
    print("Generating training data...")
    raw_data = engine.generate_data()
    
    print("Preprocessing data...")
    X, y = engine.preprocess(raw_data)
    
    print("Starting Model Competition...")
    engine.train_and_evaluate(X, y)
    
    engine.plot_importance()
    engine.save_pipeline()
    
    print("\nVerification Inference:")
    sample = {
        'district': 'Mysuru', 'area': 15.5, 'crop': 'Rice', 
        'soil_type': 'Red', 'temperature': 28.5, 
        'humidity': 65, 'rainfall': 1200, 'soil_moisture': 35
    }
    print(f"Sample Prediction: {predict_yield(sample)} tons")
