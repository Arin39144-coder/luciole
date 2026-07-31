# Utiliser l'image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances
COPY backend/requirements.txt /app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source (backend, dashboard, etc.)
COPY . /app

# Définir la variable d'environnement pour Flask
ENV FLASK_APP=backend/run.py
ENV PYTHONUNBUFFERED=1

# Exposer le port (Railway utilise le port $PORT par défaut)
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120", "backend.run:app"]