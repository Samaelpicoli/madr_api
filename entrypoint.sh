#!/bin/bash

# Espera o banco estar pronto (exemplo simples)
until pg_isready -h madr_database -p 5432 -U app_user
do
  echo "Esperando o banco ficar pronto..."
  sleep 2
done

echo "Banco pronto! Rodando migrations..."

alembic upgrade head

echo "Iniciando aplicação..."

poetry run uvicorn --host 0.0.0.0 --port 8000 madr.app:app
