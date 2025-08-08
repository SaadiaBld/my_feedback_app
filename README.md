# Mon Application Trustpilot

Ce projet est une application web qui affiche des données depuis une API, le tout servi par une application Flask.

## Architecture

*   **`app/`**: Contient l'application web Flask.
    *   **`templates/`**: Fichiers HTML pour l'interface utilisateur.
    *   **`routes/`**: Logique de routage de l'application Flask.
*   **`api/`**: Contient l'API FastAPI qui expose les données.
    *   **`routes/`**: Endpoints de l'API.
    *   **`services/`**: Logique métier pour récupérer les données (par exemple, depuis BigQuery).
*   **`run.py`**: Point d'entrée pour lancer l'application Flask.
*   **`start.sh`**: Script pour lancer l'application Flask et l'API FastAPI simultanément.

## Prérequis

*   Python 3.10 ou supérieur
*   Un environnement virtuel Python
*   Accés à un projet GCP pour BigQuery
*   Un fichier de service account avec credentials

## Installation

1.  **Clonez le dépôt :**

    ```bash
    git clone <url_du_depot>
    cd my_app_trustpilot
    ```

2.  **Créez et activez un environnement virtuel :**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Installez les dépendances :**

    ```bash
    pip install -r api/requirements.txt
    pip install -r app/requirements.txt
    pip install -r requirements-test.txt

    ```

4.  **Configurez vos identifiants Google Cloud :**

    Assurez-vous que le chemin vers votre fichier de clés de service Google Cloud est correctement configuré dans votre environnement. Vous pouvez le faire en définissant la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS`.
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/chemin/vers/votre-cle.json"
    ```

## Lancement

Pour lancer l'application Flask et l'API FastAPI, exécutez simplement le script `start.sh` :

```bash
./start.sh

```

Cela lancera :
*   L'application Flask sur `http://127.0.0.1:5000`
*   L'API FastAPI sur `http://127.0.0.1:8000`

Vous pouvez ensuite accéder à l'application web dans votre navigateur à l'adresse `http://127.0.0.1:5000`.

## Tests automatiques

Les tests sont lancés automatiquement à chaque push ou pull request sur la branche main via GitHub Actions.

    Le fichier de configuration est situé ici : .github/workflows/test.yml

    Il installe les dépendances de chaque service et lance pytest.

Vous pouvez aussi lancer les tests manuellement :

```bash

pytest -v

```