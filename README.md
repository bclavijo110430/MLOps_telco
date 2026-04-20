# MLOps Practice Project

This repository contains the structure for an MLOps pipeline, following best practices for model training, preprocessing, and deployment.

## Project Description

**MLOps Telco Churn** is a project designed to predict customer churn in the telecommunications industry. It leverages MLOps principles to ensure efficient model development, deployment, and monitoring. The project includes data preprocessing, model training, and serving through a FastAPI application, all containerized for reproducibility.

## Structure

- `data/`: Data management.
  - `raw/`: Immutable raw data.
  - `processed/`: Features ready for training.
- `src/`: Source code.
  - `preprocessing.py`: Feature engineering and data cleaning.
  - `train.py`: Model training logic.
  - `predict.py`: Inference scripts.
- `models/`: Versioned model artifacts.
- `tests/`: Unit and integration tests.
- `docker/`: Containerization for reproducibility.
- `pipelines/`: CI/CD automation.

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run preprocessing: `python src/preprocessing.py`
3. Train model: `python src/train.py`

## Serving & Model Inference (FastAPI)

La aplicación incluye un servicio de alta disponibilidad para servir el modelo entrenado.

### Despliegue del Servicio

#### Con Helm (Kubernetes - Recomendado)
```bash
helm install serving-service ./infrastructure/servingChart -n serving --create-namespace
```

#### Con Docker Compose
```bash
docker compose -f infrastructure/serving/docker-compose.yaml up --build -d
```

### Endpoints
- **Production URL (K8s):** `https://serving.bclavijo.xyz`
- `GET /health`: Verifica el estado de la API, el modelo y el escalador.
- `POST /predict`: Recibe datos numéricos y retorna la predicción de Churn.

### Guía de Uso de la API
Para consultar el modelo, debes enviar una lista de 19 características numéricas. El servicio aplica automáticamente el escalado estadístico (`StandardScaler`).

#### Mapeo de Variables Categóricas (Label Encoding)
Si tus datos originales son texto, conviértelos usando esta referencia:
- **Binarios (gender, Partner, etc):** No=0, Yes=1 (Female=0, Male=1).
- **Múltiples opciones:** Orden alfabético (Ej. PaymentMethod: Bank transfer=0, Credit card=1, etc).
- **Numéricos:** Se envían tal cual (tenure, MonthlyCharges).

**Ejemplo de conversión (Cliente 7590-VHVEG):**

| Columna Original | Valor Texto | Código Numérico | Razón |
| :--- | :--- | :--- | :--- |
| **gender** | `Female` | **0** | (Female=0, Male=1) |
| **SeniorCitizen** | `0` | **0** | (Ya es número) |
| **Partner** | `Yes` | **1** | (No=0, Yes=1) |
| **Dependents** | `No` | **0** | (No=0, Yes=1) |
| **tenure** | `1` | **1** | (Ya es número) |
| **PhoneService** | `No` | **0** | (No=0, Yes=1) |
| **MultipleLines** | `No phone service` | **1** | (No=0, No phone=1, Yes=2) |
| **InternetService** | `DSL` | **0** | (DSL=0, Fiber=1, No=2) |
| **Contract** | `Month-to-month` | **0** | (Month-to-month=0, 1yr=1, 2yr=2) |
| **MonthlyCharges** | `29.85` | **29.85** | (Valor real) |

#### Ejemplo de Consulta (CURL)
**Cliente: 7590-VHVEG (Riesgo de Abandono)**
```bash
curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{
       "data": [
         [0, 0, 1, 0, 1, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 1, 2, 29.85, 29.85]
       ]
     }'
```

**Respuesta Esperada:**
```json
{
  "predictions": [1],
  "model_version": "models:/Telco-Churn-Prediction/latest",
  "preprocessed": true
}
```

### Interpretación de Resultados
- **[0]**: El cliente NO abandonará (Loyal).
- **[1]**: El cliente TIENE RIESGO de abandonar (Churn).
