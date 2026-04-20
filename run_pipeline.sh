#!/bin/bash
set -e

# Configuración de variables
IMAGE_NAME="mlops-app"
DOCKERFILE_PATH="docker/Dockerfile"
BUILD_CONTEXT="." # Contexto de compilación (Directorio raíz)

echo "🚀 Iniciando Ciclo MLOps (Build + Preprocessing + Training)..."

# 1. Construir la imagen del proyecto
echo -e "\n🔨 [1/3] Construyendo imagen Docker..."
docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH $BUILD_CONTEXT  --no-cache

# 2. Ejecutar el Preprocesamiento
echo -e "\n🧹 [2/3] Ejecutando Preprocesamiento..."
docker run \
  -v "$(pwd)/data:/app/data" \
  $IMAGE_NAME python src/preprocessing.py

# 3. Ejecutar el Entrenamiento (MLflow Tracking)
echo -e "\n🧠 [3/3] Ejecutando Entrenamiento con MLflow..."
# Usamos --network mlflow-net para conectar con el servidor mlflow_server
docker run  \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/models:/app/models" \
  $IMAGE_NAME python src/train.py

echo -e "\n✅ Pipeline completado exitosamente."
echo "🔗 Revisa la UI de MLflow: http://localhost:5000"
