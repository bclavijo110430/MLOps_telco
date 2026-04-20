import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import mlflow
import mlflow.sklearn
import joblib
import os

def train_model(data_dir):
    # Configurar MLflow Tracking
    mlflow.set_tracking_uri("https://mlflow.bclavijo.xyz")
    # Forzamos el uso del proxy de artefactos mediante el esquema mlflow-artifacts:/
    experiment_name = "Telco-Churn-Prediction-v3"
    env_artifact_location = "mlflow-artifacts:/"
    
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
        print(f"Creating experiment {experiment_name} with location {env_artifact_location}")
        mlflow.create_experiment(experiment_name, artifact_location=env_artifact_location)
    
    mlflow.set_experiment(experiment_name)

    # Cargar datos
    print(f"Loading data from {data_dir}...")
    X_train = pd.read_csv(f"{data_dir}/X_train.csv")
    X_test = pd.read_csv(f"{data_dir}/X_test.csv")
    y_train = pd.read_csv(f"{data_dir}/y_train.csv").values.ravel()
    y_test = pd.read_csv(f"{data_dir}/y_test.csv").values.ravel()

    # Parámetros del modelo
    n_estimators = 100
    max_depth = 10

    with mlflow.start_run():
        print("Training RandomForest model...")
        model = RandomForestClassifier(
            n_estimators=n_estimators, 
            max_depth=max_depth, 
            random_state=42
        )
        model.fit(X_train, y_train)

        # Predicciones y Métricas
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f"Accuracy: {acc:.4f}")
        print(f"F1 Score: {f1:.4f}")

        # Loguear parámetros y métricas en MLflow
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)

        # Inferir la firma del modelo
        from mlflow.models.signature import infer_signature
        signature = infer_signature(X_train, model.predict(X_train))

        # Loguear el modelo y registrarlo en el Model Registry
        print(f"Artifact URI: {mlflow.get_artifact_uri()}")
        mlflow.sklearn.log_model(
            sk_model=model, 
            artifact_path="churn-model",
            registered_model_name="Telco-Churn-Prediction",
            signature=signature
        )
        
        # Guardar localmente también
        os.makedirs("mlops-project/models", exist_ok=True)
        joblib.dump(model, "mlops-project/models/model.joblib")
        
        print("Model and metrics logged to MLflow.")

if __name__ == "__main__":
    train_model("data/processed")
