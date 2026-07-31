"""Point d'entrée de l'application Luciole."""
import os
import pymysql
pymysql.install_as_MySQLdb()

from dotenv import load_dotenv

load_dotenv()

# Supprimer toute variable d'environnement problématique
os.environ.pop('SQLALCHEMY_ENGINE_OPTIONS', None)

from app import create_app, db
from app.services.seed_service import seed_initial_data

app = create_app()

# 🔥 Supprimer la clé si elle existe dans la configuration
app.config.pop('SQLALCHEMY_ENGINE_OPTIONS', None)

# Initialisation de la base de données
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