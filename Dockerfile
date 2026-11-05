
# Utiliser Python 3.12
FROM python:3.12-slim

# Éviter la création de fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Afficher directement les messages Python
ENV PYTHONUNBUFFERED=1

# Définir le dossier de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances du projet
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/

# Copier les fichiers nécessaires à Alembic
COPY alembic/ ./alembic/
COPY alembic.ini .

# Indiquer que l'API utilise le port 8000
EXPOSE 8000

# Démarrer le serveur FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
