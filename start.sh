#!/bin/bash

#!/bin/bash

# Lancer Flask en arrière-plan
python run.py &

# Lancer FastAPI
uvicorn api.main:app --host=0.0.0.0 --port=10000 &

# Attendre que l’un des deux processus s'arrête
wait -n

#bloc suivant à activer pour dev local, danc e cas, il faut commenter les lignes ci-dessus
# # Lancer l'application Flask en arrière-plan
# python run.py &

# # Lancer l'API FastAPI en arrière-plan
# uvicorn api.main:app --reload &
