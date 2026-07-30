"""Routes de défis et badges."""
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.gamification_service import BadgeService, ChallengeService

challenges_bp = Blueprint("challenges", __name__)


@challenges_bp.route("", methods=["GET"])
@jwt_required()
def list_challenges():
    user_id = int(get_jwt_identity())
    challenges = ChallengeService.get_active_challenges(user_id)
    return jsonify({"challenges": challenges}), 200


@challenges_bp.route("/badges", methods=["GET"])
@jwt_required()
def list_badges():
    user_id = int(get_jwt_identity())
    badges = BadgeService.get_user_badges(user_id)
    return jsonify({"badges": badges}), 200
