#!/bin/bash

# Asegúrate de que el script sea ejecutable
chmod +x start.sh

# Ejecuta la aplicación FastAPI usando uvicorn
uvicorn main:app --host 0.0.0.0 --port $PORT
