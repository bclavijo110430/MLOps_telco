import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

def preprocess_data(input_path, output_dir):
    print(f"Reading data from {input_path}...")
    df = pd.read_csv(input_path)

    # 1. Limpieza de datos
    # TotalCharges tiene espacios en blanco que impiden que sea float
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())

    # Eliminar ID de cliente
    df.drop('customerID', axis=1, inplace=True)

    # 2. Encoding de variables categóricas
    le = LabelEncoder()
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])

    # 3. División de datos
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Escalado
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Guardar datos procesados
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardamos como arrays de numpy para eficiencia o CSVs
    pd.DataFrame(X_train_scaled).to_csv(f"{output_dir}/X_train.csv", index=False)
    pd.DataFrame(X_test_scaled).to_csv(f"{output_dir}/X_test.csv", index=False)
    y_train.to_csv(f"{output_dir}/y_train.csv", index=False)
    y_test.to_csv(f"{output_dir}/y_test.csv", index=False)

    # Guardar scaler para inferencia real-time
    joblib.dump(scaler, f"{output_dir}/scaler.joblib")
    
    print(f"Preprocessing completed. Files saved in {output_dir}")

if __name__ == "__main__":
    preprocess_data(
        "data/raw/telco_churn.csv", 
        "data/processed"
    )
