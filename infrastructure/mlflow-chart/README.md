# MLflow Kubernetes Chart

Chart de Helm para desplegar MLflow con PostgreSQL como backend de metadatos de forma nativa en Kubernetes. Diseñado siguiendo guías de SRE e "Infrastructure as Code" (IaC) para fácil acoplamiento con controladores GitOps.

## Componentes

- **MLflow Tracking Server:** Desplegado mediante K8s `Deployment`. Servidor principal de tracking de experimentos. Almacena artefactos en un PVC adjunto.
- **PostgreSQL:** Desplegado mediante K8s `StatefulSet`. Actúa como backend-store relacional para guardar métricas, parámetros y metadatos.

## Requisitos

- Clúster de K8s operativo (e.g., `minikube -p mlflow`).
- Helm v3+.
- Default `StorageClass` aprovisionado para el bindings de los PVCs.

## Instalación (Comandos Imperativos)

> **Nota:** Para entornos productivos se asume que este chart se gestionará desde tu repositorio vía ArgoCD o Flux.

1. **Situarse en la raíz de infraestructura:**
   ```bash
   cd infrastructure
   ```

2. **Instalar el chart en un namespace dedicado:**
   ```bash
   helm upgrade --install mi-mlflow ./mlflow-chart \
     --namespace mlops \
     --create-namespace
   ```

3. **Verificar el despliegue:**
   Asegurarse de que tanto base de datos como servidor MLflow levanten correctamente:
   ```bash
   kubectl get pods -n mlops -w
   ```

## Acceso Interfaz de MLflow

Una vez que los pods estén en estado `Running`, puedes acceder a través del IP del nodo y el NodePort definido (default: 30000):

### Usando Minikube:
```bash
minikube -p mlflow service mi-mlflow-mlflow -n mlops --url
```

### Acceso Manual:
Obtén la IP del nodo y el puerto:
```bash
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
NODE_PORT=$(kubectl get svc mi-mlflow-mlflow -n mlops -o jsonpath='{.spec.ports[0].nodePort}')
echo "http://$NODE_IP:$NODE_PORT"
```

## Manejo de Secretos y Persistencia

### Secretos (Best Practices)
Nunca versiones contraseñas en plano en el `values.yaml`. El template incluye una condicional segura:
- Crea un secreto en K8s a través de tu flujo preferido (e.g., `ExternalSecrets` o `SealedSecrets`).
- Modifica los values indicando el nombre del secreto ya existente:
  ```yaml
  postgresql:
    existingSecret: "nombre-de-tu-secreto"
  ```
Esto deshabilita la generación automática del secreto local evitando hardcoding.

### Persistencia de Datos
Los volúmenes (Artefactos de MLflow y DB de pgdata) no se limpian de manera predeterminada en un `helm uninstall`. En caso de querer destruir la persistencia totalmente en entornos dev:
```bash
kubectl delete pvc -l app.kubernetes.io/name=mlflow -n mlops
kubectl delete pvc -l app.kubernetes.io/name=mlflow-postgresql -n mlops
```
