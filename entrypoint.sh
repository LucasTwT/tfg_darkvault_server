#!/bin/bash
set -e  

echo "Aplicando migraciones con Alembic..."
cd app/db
alembic upgrade head

cd ..

cd ..

echo "Iniciando FastAPI con Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload