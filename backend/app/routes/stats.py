"""Routes de statistiques."""
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.advice_engine import AdviceEngine
from app.services.gamification_service import BadgeService, ChallengeService
from app.services.reflection_score_service import ReflectionScoreService
from app.services.stats_service import StatsService

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/today", methods=["GET"])
@jwt_required()
def today():
    user_id = int(get_jwt_identity())
    stats = StatsService.today_stats(user_id)
    score = ReflectionScoreService.get_latest(user_id)
    challenge = ChallengeService.assign_daily_challenge(user_id)

    return jsonify({
        "stats": stats,
        "score": score,
        "current_challenge": challenge,
    }), 200


@stats_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    today = StatsService.today_stats(user_id)
    dashboard_data = StatsService.dashboard_stats(user_id)
    score = ReflectionScoreService.get_latest(user_id) or ReflectionScoreService.calculate(user_id)
    score_history = ReflectionScoreService.get_history(user_id, days=30)
    advice = AdviceEngine.get_advice(user_id)
    badges = BadgeService.get_user_badges(user_id)
    challenges = ChallengeService.get_active_challenges(user_id)

    return jsonify({
        "today": today,
        "dashboard": dashboard_data,
        "score": score,
        "score_history": score_history,
        "advice": advice,
        "badges": badges,
        "challenges": challenges,
    }), 200
