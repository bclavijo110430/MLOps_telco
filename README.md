# Proyecto de Práctica MLOps

Este repositorio contiene la estructura para un pipeline de MLOps, siguiendo las mejores prácticas para el entrenamiento, preprocesamiento y despliegue de modelos.

## Descripción del Proyecto

**MLOps Telco Churn** es un proyecto diseñado para predecir el abandono de clientes (churn) en la industria de las telecomunicaciones. Utiliza principios de MLOps para asegurar un desarrollo, despliegue y monitoreo eficiente de los modelos. El proyecto incluye el preprocesamiento de datos, el entrenamiento del modelo y el servicio a través de una aplicación FastAPI, todo contenedorizado para asegurar la reproducibilidad.

## Estructura

- `data/`: Gestión de datos.
  - `raw/`: Datos brutos inmutables.
  - `processed/`: Características listas para el entrenamiento.
- `src/`: Código fuente.
  - `preprocessing.py`: Ingeniería de características y limpieza de datos.
  - `train.py`: Lógica de entrenamiento del modelo.
  - `predict.py`: Scripts de inferencia.
- `models/`: Artefactos de modelos versionados.
- `tests/`: Pruebas unitarias y de integración.
- `docker/`: Contenedores para reproducibilidad.
- `infrastructure/`: Manifiestos de infraestructura y Helm charts.

## Primeros Pasos

1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar preprocesamiento: `python src/preprocessing.py`
3. Entrenar el modelo: `python src/train.py`

## Serving e Inferencia de Modelos (FastAPI)

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
- **URL de Producción (K8s):** `https://serving.bclavijo.xyz`
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
- **[0]**: El cliente NO abandonará .
- **[1]**: El cliente TIENE RIESGO de abandonar.
