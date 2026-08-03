"""Routes d'authentification."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app import db
from app.models import User, UserGoal
from app.utils.security import (
    check_password,
    hash_password,
    validate_email_address,
    validate_password,
    validate_username,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    valid, msg = validate_username(username)
    if not valid:
        return jsonify({"error": msg}), 400

    valid, msg = validate_email_address(email)
    if not valid:
        return jsonify({"error": msg}), 400

    valid, msg = validate_password(password)
    if not valid:
        return jsonify({"error": msg}), 400

    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        return jsonify({"error": "Nom d'utilisateur ou email déjà utilisé."}), 409

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.flush()  # pour obtenir l'id
    
    # Vérifier si un objectif existe déjà (pour éviter la duplication)
    existing_goal = UserGoal.query.filter_by(user_id=user.id).first()
    if not existing_goal:
        goal = UserGoal(user_id=user.id, daily_limit=120)
        db.session.add(goal)
    
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Inscription réussie.",
        "access_token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({"error": "Identifiants invalides."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Connexion réussie.",
        "access_token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404
    return jsonify({"user": user.to_dict()}), 200
