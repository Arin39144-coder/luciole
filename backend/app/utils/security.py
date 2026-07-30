"""Utilitaires de sécurité et validation."""
import re

import bcrypt
from email_validator import EmailNotValidError, validate_email


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def validate_username(username: str) -> tuple[bool, str]:
    if not username or len(username.strip()) < 3:
        return False, "Le nom d'utilisateur doit contenir au moins 3 caractères."
    if len(username) > 80:
        return False, "Le nom d'utilisateur ne peut pas dépasser 80 caractères."
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return False, "Caractères autorisés : lettres, chiffres, _ et -."
    return True, ""


def validate_email_address(email: str) -> tuple[bool, str]:
    try:
        validate_email(email, check_deliverability=False)
        return True, ""
    except EmailNotValidError as exc:
        return False, str(exc)


def validate_password(password: str) -> tuple[bool, str]:
    if not password or len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."
    if len(password) > 128:
        return False, "Le mot de passe est trop long."
    return True, ""


VALID_REASONS = {
    "etudes", "travail", "programmation", "recherche", "creativite", "divertissement", "autre"
}
VALID_NEEDS_AI = {"yes", "no", "partially"}

REASON_LABELS = {
    "etudes": "Études",
    "travail": "Travail",
    "programmation": "Programmation",
    "recherche": "Recherche",
    "creativite": "Créativité",
    "divertissement": "Divertissement",
    "autre": "Autre",
}
