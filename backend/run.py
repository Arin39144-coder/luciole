"""Point d'entrée de l'application Luciole."""
import os
import pymysql
pymysql.install_as_MySQLdb()

from dotenv import load_dotenv

load_dotenv()

# 🔥 Supprimer TOUTE variable d'environnement qui pourrait interférer
os.environ.pop('SQLALCHEMY_ENGINE_OPTIONS', None)

# Création de l'application
from app import create_app, db
from app.services.seed_service import seed_initial_data

app = create_app()

# 🔥 Forcer la valeur dans la configuration de l'app AVANT toute utilisation
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

# Initialisation de la base de données avec gestion d'erreur
with app.app_context():
    try:
        # Vérifier que la clé est bien un dictionnaire
        if not isinstance(app.config.get('SQLALCHEMY_ENGINE_OPTIONS'), dict):
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
            print("✅ Forcé SQLALCHEMY_ENGINE_OPTIONS à un dictionnaire.")

        db.create_all()
        seed_initial_data()
        print("✅ Base de données initialisée avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de la base de données : {e}")
        # On continue pour que l'application démarre quand même
        # (la base pourra être créée plus tard via une route dédiée si besoin)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")