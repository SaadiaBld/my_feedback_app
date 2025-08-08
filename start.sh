#!/bin/bash
#uvicorn api.run:app --host=0.0.0.0 --port=$PORT   #port injecté par render

#!/bin/bash
# Script pour démarrer l'application Flask et FastAPI en local 

echo "Démarrage en local..."

# Pour Flask < 2.2
export FLASK_APP=app.run_app
export FLASK_DEBUG=1 # Activer le mode debug pour Flask

# Lancer Flask
flask run --host=0.0.0.0 --port=5000 &


# Lancer FastAPI
uvicorn api.main:app --host=0.0.0.0 --port=10000 &

# Attendre que l’un des deux processus s'arrête
wait -n
