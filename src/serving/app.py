from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import mlflow.pyfunc
import pandas as pd
import os
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MLOps Prediction Service",
    description="API para servir modelos de MLflow",
    version="1.0.0"
)

import joblib

# Configuración de MLflow y Scaler
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_URI = os.getenv("MODEL_URI", "models:/Telco-Churn-Prediction/latest")
SCALER_PATH = os.getenv("SCALER_PATH", "/app/data/processed/scaler.joblib")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Variables globales para el modelo y el scaler
model = None
scaler = None

@app.on_event("startup")
def load_artifacts():
    global model, scaler
    # Cargar Modelo
    try:
        logger.info(f"Cargando modelo desde: {MODEL_URI}")
        model = mlflow.pyfunc.load_model(MODEL_URI)
        logger.info("Modelo cargado exitosamente.")
    except Exception as e:
        logger.error(f"Error cargando el modelo: {e}")

    # Cargar Scaler
    try:
        if os.path.exists(SCALER_PATH):
            logger.info(f"Cargando scaler desde: {SCALER_PATH}")
            scaler = joblib.load(SCALER_PATH)
            logger.info("Scaler cargado exitosamente.")
        else:
            logger.warning(f"No se encontró el scaler en {SCALER_PATH}. Las predicciones podrían fallar.")
    except Exception as e:
        logger.error(f"Error cargando el scaler: {e}")

class PredictionInput(BaseModel):
    data: list  # Puede ser una lista de listas (numérico) o lista de dicts (requiere nombres)

@app.get("/health")
def health_check():
    """Endpoint de salud para Liveness/Readiness probes."""
    if model is None or scaler is None:
        status = "unhealthy"
        error = "Model or Scaler not loaded"
        return JSONResponse(content={"status": status, "error": error}, status_code=503)
    
    return {
        "status": "healthy", 
        "model_uri": MODEL_URI,
        "scaler_path": SCALER_PATH
    }

@app.post("/predict")
def predict(input_data: PredictionInput):
    """Realiza predicciones aplicando el escalado automáticamente."""
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Servicio no disponible (modelo o scaler sin cargar)")
    
    try:
        # 1. Convertir entrada a DataFrame
        df = pd.DataFrame(input_data.data)
        
        # 2. Aplicar escalado
        # Nota: Asume que los datos ya vienen codificados numéricamente pero sin escalar
        scaled_data = scaler.transform(df)
        
        # 3. Convertir a DataFrame con nombres de columnas como strings para cumplir con la firma de MLflow
        feature_names = [str(i) for i in range(scaled_data.shape[1])]
        scaled_df = pd.DataFrame(scaled_data, columns=feature_names)
        
        # 4. Predecir
        predictions = model.predict(scaled_df)
        
        return {
            "predictions": predictions.tolist(),
            "model_version": MODEL_URI,
            "preprocessed": True
        }
    except Exception as e:
        logger.error(f"Error durante el procesamiento/predicción: {e}")
        raise HTTPException(status_code=400, detail=f"Error en datos de entrada: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
