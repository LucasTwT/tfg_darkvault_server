# Imagen base
FROM python:3.11-slim

# Setear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (ej: psycopg2, bash, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cacheo)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

# Dar permisos de ejecución al entrypoint
RUN chmod +x entrypoint.sh


# Comando por defecto
CMD ["./entrypoint.sh"]
