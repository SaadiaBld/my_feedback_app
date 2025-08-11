tests flask_routes.py qui est long, voir pour isoler le test fautif 

- name: Run API tests
  run: pytest -vv tests/test_api_* --durations=10 --timeout=30 --timeout-method=thread
- name: Run Flask tests
  run: pytest -vv tests/test_flask_routes.py --durations=10 --timeout=30 --timeout-method=thread
