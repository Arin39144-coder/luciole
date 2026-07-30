"""Routes de gestion des objectifs."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import UserGoal

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("", methods=["GET"])
@jwt_required()
def get_goal():
    user_id = int(get_jwt_identity())
    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if not goal:
        goal = UserGoal(user_id=user_id, daily_limit=120)
        db.session.add(goal)
        db.session.commit()
    return jsonify({"goal": goal.to_dict()}), 200


@goals_bp.route("", methods=["PUT"])
@jwt_required()
def update_goal():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    daily_limit = data.get("daily_limit")

    if daily_limit is None or not isinstance(daily_limit, int) or daily_limit < 15 or daily_limit > 720:
        return jsonify({"error": "daily_limit doit être entre 15 et 720 minutes."}), 400

    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if not goal:
        goal = UserGoal(user_id=user_id)
        db.session.add(goal)

    goal.daily_limit = daily_limit
    db.session.commit()

    return jsonify({"message": "Objectif mis à jour.", "goal": goal.to_dict()}), 200
