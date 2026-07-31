FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Important : on se place dans le dossier backend
WORKDIR /app/backend

ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# La commande s'exécute maintenant dans /app/backend
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120", "run:app"]