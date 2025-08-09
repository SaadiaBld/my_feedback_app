#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
exec gunicorn --bind 0.0.0.0:$PORT run_app:app