FROM python:3.10-slim

WORKDIR /app

# Dependencias necesarias para scikit-learn y psycogp2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Los scripts están en src/, los datos en data/
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "src/train.py"]
