#!/bin/bash

# Lancer l'application Flask en arrière-plan
python run.py &

# Lancer l'API FastAPI en arrière-plan
uvicorn api.main:app --reload &
