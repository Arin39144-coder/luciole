import os

workers = int(os.getenv("GUNICORN_WORKERS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Pour éviter les problèmes de chargement en mode production
worker_class = "sync"