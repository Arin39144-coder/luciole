#!/bin/sh
set -e

# Attendre que MySQL soit prêt (si on utilise docker-compose)
# Mais sur Render, la base est externe, on ne fait rien.

# Lancer les migrations (create_all est déjà appelé dans create_app)
# On peut forcer la création des tables
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app import db; db.create_all(); from app.services.seed_service import seed_initial_data; seed_initial_data()"

exec "$@"