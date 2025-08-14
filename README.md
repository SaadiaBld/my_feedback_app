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

## Chaîne d'Intégration et de Déploiement Continu (CI/CD)

Ce projet utilise une chaîne de CI/CD automatisée grâce à **GitHub Actions**. Le workflow complet est défini dans le fichier [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml).

### Outils utilisés

*   **GitHub Actions** : Orchestrateur de la chaîne CI/CD.
*   **Python & Pytest** : Pour l'exécution des tests unitaires et d'intégration.
*   **Render** : Plateforme d'hébergement pour l'application et l'API, dont les déploiements sont déclenchés par des webhooks.
*   **cURL** : Utilisé pour appeler les webhooks de déploiement de Render.

### Déclencheurs de la chaîne (Triggers)

Le workflow est conçu pour s'adapter au cycle de vie du développement :

1.  **Sur une Pull Request vers `main`** (`pull_request`) :
    *   **Action :** Le workflow lance uniquement l'étape de tests (`test`).
    *   **Objectif :** Valider que les changements proposés n'introduisent pas de régression avant de les fusionner. Le déploiement n'est pas exécuté.

2.  **Sur un push vers `main`** (`push`) :
    *   **Action :** Le workflow exécute la chaîne complète : tests, puis déploiement, puis tests de fumée.
    *   **Objectif :** Après la fusion (merge) d'une Pull Request, le code validé est automatiquement déployé en production.

3.  **Manuellement** (`workflow_dispatch`) :
    *   **Action :** Le workflow peut être lancé manuellement depuis l'onglet "Actions" de GitHub.
    *   **Objectif :** Permettre de redéployer la version actuelle de `main` en cas de besoin, sans avoir à faire un nouveau commit.

### Étapes et Tâches de la chaîne (Jobs)

La chaîne est composée de trois jobs séquentiels qui dépendent les uns des autres :

#### 1. `test`
*   **Tâches :**
    1.  Récupère le code source (`checkout`).
    2.  Configure l'environnement Python.
    3.  Installe toutes les dépendances du projet (`pip install`).
    4.  Démarre un service de base de données PostgreSQL temporaire pour les tests.
    5.  Lance la suite de tests complète avec `pytest`.
*   **Condition :** S'exécute à chaque `pull_request` ou `push` sur `main`.

#### 2. `deploy`
*   **Dépendance :** Ne se lance que si le job `test` a réussi.
*   **Condition :** Ne s'exécute que lors d'un `push` sur `main` (ou un lancement manuel).
*   **Tâches :**
    1.  Appelle le webhook de déploiement de l'API sur Render.
    2.  Appelle le webhook de déploiement de l'application web sur Render.

#### 3. `smoke-test`
*   **Dépendance :** Ne se lance que si le job `deploy` a été déclenché.
*   **Condition :** Ne s'exécute que lors d'un `push` sur `main` (ou un lancement manuel).
*   **Tâches :**
    1.  Attend 30 secondes pour laisser le temps aux services de redémarrer sur Render.
    2.  Vérifie à intervalle régulier les points de terminaison de santé (`/health` et `/healthz`) de l'API et de l'application pour s'assurer qu'elles sont bien en ligne après le déploiement.

## Tests automatiques

Les tests sont lancés automatiquement à chaque push ou pull request sur la branche main via GitHub Actions.

    Le fichier de configuration est situé ici : .github/workflows/test.yml

    Il installe les dépendances de chaque service et lance pytest.

Vous pouvez aussi lancer les tests manuellement :

```bash

pytest -v

```
