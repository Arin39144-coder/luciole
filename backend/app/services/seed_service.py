"""Données initiales (plateformes, défis, badges)."""
from app import db
from app.models import AIPlatform, Badge, Challenge


def seed_initial_data():
    platforms = [
        ("ChatGPT OpenAI", "chat.openai.com"),
        ("ChatGPT", "chatgpt.com"),
        ("Claude", "claude.ai"),
        ("Gemini", "gemini.google.com"),
        ("Copilot", "copilot.microsoft.com"),
        ("Perplexity", "perplexity.ai"),
        ("Poe", "poe.com"),
        ("DeepSeek", "deepseek.com"),
    ]
    for name, url in platforms:
        if not AIPlatform.query.filter_by(name=name).first():
            db.session.add(AIPlatform(name=name, url=url))

    challenges = [
        ("Réflexion 24h", "Réfléchir avant chaque utilisation pendant 24h", "daily", 15),
        ("Réduction 10%", "Réduire son temps IA de 10% par rapport à hier", "daily", 20),
        ("Semaine consciente", "Utiliser l'IA de façon consciente pendant 7 jours", "weekly", 50),
        ("Pause nocturne", "Éviter l'IA entre 22h et 7h pendant 3 jours", "weekly", 30),
    ]
    for title, desc, ctype, reward in challenges:
        if not Challenge.query.filter_by(title=title).first():
            db.session.add(Challenge(title=title, description=desc, type=ctype, reward=reward))

    badges = [
        ("Premier pas", "Première session enregistrée avec réflexion", "star"),
        ("3 jours conscients", "3 jours consécutifs avec score > 40", "calendar"),
        ("Une semaine maîtrisée", "7 jours consécutifs avec score > 60", "trophy"),
        ("Réduction 50%", "Réduction de 50% du temps IA sur une semaine", "leaf"),
        ("Utilisateur réfléchi", "Score supérieur à 80 pendant 5 jours", "brain"),
    ]
    for name, desc, icon in badges:
        if not Badge.query.filter_by(name=name).first():
            db.session.add(Badge(name=name, description=desc, icon=icon))

    db.session.commit()
