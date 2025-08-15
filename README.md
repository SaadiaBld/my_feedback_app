# Mon Application Trustpilot

Ce projet est une application web qui affiche des données depuis une API, le tout servi par une application Flask.

## Architecture

*   **`app/`**: Contient l'application web Flask.
    *   **`templates/`**: Fichiers HTML pour l'interface utilisateur.
    *   **`routes/`**: Logique de routage de l'application Flask.
    *   **`run_app.py`**: Point d'entrée pour lancer l'application Flask (utilisé par Gunicorn).
*   **`api/`**: Contient l'API FastAPI qui expose les données.
    *   **`routes/`**: Endpoints de l'API.
    *   **`services/`**: Logique métier pour récupérer les données (par exemple, depuis BigQuery).
    *   **`db_models.py`**: Modèles de base de données spécifiques à l'API.
    *   **`database.py`**: Configuration de la connexion à la base de données pour l'API.
    *   **`deps.py`**: Dépendances FastAPI (incluant la session DB).
*   **`.env`**: Fichier de configuration des variables d'environnement locales (non versionné).
*   **`start.sh`**: Script pour lancer l'application Flask et l'API FastAPI simultanément en local.

## Prérequis

*   Python 3.10 ou supérieur
*   Un environnement virtuel Python
*   Accès à un projet GCP pour BigQuery
*   Un fichier de service account avec credentials Google Cloud

## Installation

1.  **Clonez le dépôt :**

    ```bash
    git clone <url_du_depot>
    cd my_feedback_app_clean # Assurez-vous d'être dans le bon répertoire
    ```

2.  **Créez et activez un environnement virtuel :**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Installez toutes les dépendances :**

    ```bash
    pip install -r requirements-test.txt
    ```
    *(Ce fichier contient toutes les dépendances nécessaires pour l'application, l'API et les tests.)*

4.  **Configurez vos variables d'environnement locales (`.env`) :**

    Créez un fichier nommé `.env` à la racine de votre projet (s'il n'existe pas). Ce fichier est ignoré par Git et contient vos configurations sensibles ou spécifiques à votre environnement local.

    ```dotenv
    # Variables d'environnement pour le développement local

    # Configuration de la base de données PostgreSQL (si non définie par DATABASE_URL)
    POSTGRES_USER=votre_utilisateur_db
    POSTGRES_PASSWORD=votre_mot_de_passe_db
    POSTGRES_DB=votre_nom_db
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432

    # Clé secrète pour les sessions Flask et la signature JWT (changez-la !)
    SECRET_KEY=une_cle_secrete_tres_longue_et_complexe

    # Chemin vers votre fichier de clés de service Google Cloud (pour l'API locale)
    # Exemple : GOOGLE_APPLICATION_CREDENTIALS=./credentials/ma-cle-gcp.json
    GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/votre-cle-gcp.json

    # URL de base de l'API pour l'application Flask (doit correspondre au port de l'API)
    API_BASE_URL=http://127.0.0.1:10000

    # Environnement (pour le débogage local)
    ENV=dev
    ```
    *Assurez-vous de remplacer les valeurs par les vôtres.*

5.  **Initialisez la base de données et créez un utilisateur de test (local) :**

    ```bash
    # Crée les tables de la base de données
    python create_tables.py

    # Crée un utilisateur de test (email: test@example.com, mdp: password)
    python create_users.py
    ```
    *(Ces scripts sont idempotents et peuvent être exécutés plusieurs fois sans problème.)*

## Lancement en local

Pour lancer l'application Flask et l'API FastAPI, exécutez simplement le script `start.sh` :

```bash
./start.sh
```

Cela lancera :
*   L'application Flask sur `http://127.0.0.1:5000`
*   L'API FastAPI sur `http://127.0.0.1:10000`

Vous pouvez ensuite accéder à l'application web dans votre navigateur à l'adresse `http://127.0.0.1:5000`.

## Chaîne d'Intégration et de Déploiement Continu (CI/CD)

Ce projet utilise une chaîne de CI/CD automatisée grâce à **GitHub Actions**. Le workflow complet est défini dans le fichier [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml).

### Outils utilisés

*   **GitHub Actions** : Orchestrateur de la chaîne CI/CD.
*   **Python & Pytest** : Pour l'exécution des tests unitaires et d'intégration.
*   **Render** : Plateforme d'hébergement pour l'application et l'API.
*   **cURL** : Utilisé pour appeler les webhooks de déploiement de Render.

### Configuration Requise sur Render

Pour que le déploiement fonctionne sur Render, vous devez configurer les variables d'environnement directement dans le tableau de bord de chaque service Render.

**Pour le service de l'application Flask (ex: `trustpilot-app`) :**

*   `ENV`: `prod`
*   `SECRET_KEY`: La même clé secrète que dans votre `.env` local.
*   `DATABASE_URL`: L'URL de connexion à votre base de données PostgreSQL sur Render (Render la fournit).
*   `RENDER`: `true` (souvent défini automatiquement par Render).

**Pour le service de l'API FastAPI (ex: `trustpilot-api`) :**

*   `ENV`: `prod`
*   `SECRET_KEY`: La même clé secrète que dans votre `.env` local.
*   `DATABASE_URL`: L'URL de connexion à votre base de données PostgreSQL sur Render (Render la fournit).
*   `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Le **contenu complet** de votre fichier de clés JSON Google Cloud.

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
