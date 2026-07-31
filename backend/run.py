"""Point d'entrée de l'application Luciole."""
import os
import sys
import pymysql
pymysql.install_as_MySQLdb()

# 🔥 Supprimer la variable d'environnement avant tout
os.environ.pop('SQLALCHEMY_ENGINE_OPTIONS', None)

from dotenv import load_dotenv
load_dotenv()

# Vérification : supprimer à nouveau si elle a été chargée
os.environ.pop('SQLALCHEMY_ENGINE_OPTIONS', None)

from app import create_app, db
from app.services.seed_service import seed_initial_data

app = create_app()

# 🔥 Forcer la clé à un dictionnaire vide dans la configuration de l'app
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

print(f"✅ SQLALCHEMY_ENGINE_OPTIONS = {app.config.get('SQLALCHEMY_ENGINE_OPTIONS')} (type: {type(app.config.get('SQLALCHEMY_ENGINE_OPTIONS'))})")

with app.app_context():
    try:
        db.create_all()
        seed_initial_data()
        print("✅ Base de données initialisée avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de la base de données : {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")