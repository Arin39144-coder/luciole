"""Point d'entrée de l'application Luciole."""
import os
import pymysql  # <-- AJOUTER
pymysql.install_as_MySQLdb()  # <-- AJOUTER

from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")