# Atelier de couture API

API REST de gestion d'un atelier de couture développée avec **FastAPI**, **Python 3.12** et **PostgreSQL**.

Cette application permet de gérer les activités quotidiennes d'un atelier de couture : clients, mesures, commandes, types de vêtements, paiements, livraisons et utilisateurs.

## Fonctionnalités principales

- Authentification sécurisée avec JWT.
- Gestion des utilisateurs et des rôles.
- Gestion des clients.
- Gestion des mesures des clients et de leur historique.
- Gestion du catalogue des types de vêtements.
- Création et suivi des commandes.
- Gestion des paiements.
- Gestion des livraisons.
- Consultation des statistiques de l'atelier.
- Contrôle des autorisations selon le rôle de l'utilisateur.

### Rôles utilisateurs

L'application distingue trois rôles :

- **Administrateur** : accès à l'ensemble des fonctionnalités et aux statistiques.
- **Accueil** : gestion des clients, commandes, paiements et livraisons.
- **Tailleur** : gestion des mesures et progression des commandes dans les étapes de confection.

## Technologies utilisées

| Technologie    | Utilisation                   |
| -------------- | ----------------------------- |
| Python 3.12    | Langage de programmation      |
| FastAPI        | Création de l'API REST        |
| Uvicorn        | Serveur d'exécution ASGI      |
| PostgreSQL 16  | Base de données relationnelle |
| SQLAlchemy 2   | ORM et accès aux données      |
| Alembic        | Gestion des migrations        |
| Pydantic 2     | Validation des données        |
| PyJWT          | Gestion des jetons JWT        |
| Argon2         | Hachage des mots de passe     |
| Pytest         | Tests automatisés             |
| Docker         | Conteneurisation              |
| Docker Compose | Orchestration des conteneurs  |

Les versions exactes des bibliothèques Python sont définies dans `requirements.txt`.

## Architecture du projet

```text
atelier-couture-api/
│
├── app/
│   ├── main.py
│   ├── seed.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
│
├── alembic/
├── scripts/
├── tests/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Organisation des couches

- `core/` : configuration, sécurité, authentification JWT et dépendances.
- `db/` : configuration de la connexion à PostgreSQL.
- `models/` : modèles représentant les tables de la base de données.
- `schemas/` : schémas Pydantic pour valider les données entrantes et sortantes.
- `routers/` : routes et endpoints de l'API.
- `services/` : logique métier de l'application.
- `alembic/` : migrations de la base de données.
- `tests/` : tests automatisés.
- `scripts/` : scripts complémentaires du projet.

## Prérequis

Pour installer et exécuter le projet, il faut disposer de :

- Python 3.12.
- PostgreSQL, si l'application est lancée sans Docker.
- Docker Desktop avec Docker Compose, pour le lancement conteneurisé.
- Git.

## Installation et configuration

### 1. Récupérer le projet

```bash
git clone https://github.com/binetouwahab/atelier-couture-api.git
cd atelier-couture-api
```

### 2. Créer un environnement virtuel

Sous Windows :

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer le fichier `.env` à partir du modèle fourni :

```cmd
copy .env.example .env
```

Modifier ensuite les valeurs dans `.env` :

- `DATABASE_URL` : adresse de connexion à PostgreSQL.
- `SECRET_KEY` : clé secrète utilisée pour les jetons JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES` : durée de validité des jetons.
- `ADMIN_EMAIL` : adresse électronique du premier administrateur.
- `ADMIN_NOM_COMPLET` : nom du premier administrateur.
- `ADMIN_MOT_DE_PASSE` : mot de passe du premier administrateur.
- `POSTGRES_USER`, `POSTGRES_PASSWORD` et `POSTGRES_DB` : paramètres PostgreSQL utilisés par Docker Compose.

**Important :** le fichier `.env` contient des informations sensibles. Il ne doit jamais être publié sur GitHub.

## Lancement sans Docker

Pour lancer l'application directement sur la machine :

1. Installer et démarrer PostgreSQL.
2. Créer la base de données et configurer `DATABASE_URL` dans `.env`.
3. Appliquer les migrations :

```bash
alembic upgrade head
```

4. Initialiser le premier administrateur et le catalogue :

```bash
python -m app.seed
```

5. Démarrer le serveur :

```bash
uvicorn app.main:app --reload
```

L'API sera accessible à l'adresse :

http://localhost:8000

## Lancement avec Docker Compose

Docker Compose permet de démarrer automatiquement l'API et PostgreSQL dans deux conteneurs distincts.

### 1. Préparer la configuration

Vérifier que le fichier `.env` existe et que les variables PostgreSQL et administrateur sont renseignées.

### 2. Construire et démarrer les conteneurs

À la racine du projet, exécuter :

```bash
docker compose up --build -d
```

Le démarrage comprend :

- La création du conteneur PostgreSQL.
- L'attente de la disponibilité de PostgreSQL grâce au healthcheck.
- La construction de l'image FastAPI.
- L'exécution des migrations Alembic.
- Le démarrage du serveur Uvicorn.

### 3. Initialiser les données

Créer le premier administrateur et les types de vêtements :

```bash
docker compose exec api python -m app.seed
```

### 4. Vérifier les conteneurs

```bash
docker compose ps
```

### 5. Consulter les journaux

```bash
docker compose logs api
```

### 6. Arrêter les conteneurs

```bash
docker compose down
```

Les données PostgreSQL sont conservées dans un volume Docker nommé `postgres_data`.

**Attention :** `docker compose down -v` supprime également ce volume et donc les données qu'il contient.

## Documentation de l'API

L'API propose une documentation interactive générée automatiquement par FastAPI.

| Adresse                      | Description                            |
| ---------------------------- | -------------------------------------- |
| http://localhost:8000/docs   | Documentation Swagger UI               |
| http://localhost:8000/health | Vérification de l'API et de PostgreSQL |

Les routes métier sont regroupées sous le préfixe `/api/v1`.

### Domaines fonctionnels

- Authentification
- Utilisateurs
- Clients
- Types de vêtements
- Mesures
- Commandes
- Paiements
- Livraisons
- Statistiques

La route `/health` est accessible directement, sans préfixe `/api/v1`.

## Authentification

L'API utilise des jetons JWT pour sécuriser les accès.

Pour utiliser les endpoints protégés :

1. Ouvrir la documentation Swagger.
2. Utiliser l'endpoint de connexion.
3. Récupérer le jeton d'accès retourné.
4. Cliquer sur le bouton **Authorize** dans Swagger.
5. Fournir le jeton pour accéder aux routes autorisées.

Les droits d'accès dépendent du rôle de l'utilisateur connecté.

## Migrations de la base de données

Les migrations sont gérées avec Alembic.

Appliquer les migrations :

```bash
alembic upgrade head
```

Consulter la migration actuellement appliquée :

```bash
alembic current
```

Consulter la migration principale :

```bash
alembic heads
```

Dans Docker, les migrations sont exécutées automatiquement au démarrage du conteneur API.

## Tests

Les tests automatisés sont exécutés avec Pytest.

Pour lancer l'ensemble des tests :

```bash
python -m pytest -v
```

## Sécurité

Quelques précautions importantes :

- Les mots de passe sont hachés avec Argon2.
- L'authentification utilise des jetons JWT.
- Les permissions sont contrôlées selon les rôles.
- Les informations sensibles sont stockées dans `.env`.
- Le fichier `.env` est exclu du dépôt Git.
- Les accès à la base de données sont réalisés avec SQLAlchemy.

## Auteure

aminatou B W Ndiaye
