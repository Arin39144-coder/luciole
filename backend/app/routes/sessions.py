"""Routes de gestion des sessions IA."""
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import AIPlatform, AISession, ReflectionAnswer
from app.services.gamification_service import BadgeService, ChallengeService
from app.services.reflection_score_service import ReflectionScoreService
from app.services.stats_service import StatsService
from app.utils.security import VALID_NEEDS_AI, VALID_REASONS

sessions_bp = Blueprint("sessions", __name__)


def _get_platform(platform_name: str, platform_url: str) -> AIPlatform:
    """Trouve ou crée une plateforme IA."""
    platform = AIPlatform.query.filter(
        AIPlatform.url.contains(platform_url.replace("www.", ""))
    ).first()
    if not platform:
        platform = AIPlatform(name=platform_name or platform_url, url=platform_url)
        db.session.add(platform)
        db.session.flush()
    return platform


@sessions_bp.route("/start", methods=["POST"])
@jwt_required()
def start_session():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    platform_name = data.get("platform_name", "Unknown")
    platform_url = data.get("platform_url", "")
    reason = (data.get("reason") or "").lower()
    needs_ai = (data.get("needs_ai") or "").lower()
    reflections = data.get("reflections", [])

    if reason and reason not in VALID_REASONS:
        return jsonify({"error": f"Raison invalide. Valeurs: {', '.join(VALID_REASONS)}"}), 400
    if needs_ai and needs_ai not in VALID_NEEDS_AI:
        return jsonify({"error": f"Valeur needs_ai invalide. Valeurs: {', '.join(VALID_NEEDS_AI)}"}), 400

    platform = _get_platform(platform_name, platform_url)

    session = AISession(
        user_id=user_id,
        platform_id=platform.id,
        start_time=datetime.utcnow(),
        reason=reason or None,
        needs_ai=needs_ai or None,
    )
    db.session.add(session)
    db.session.flush()

    for ref in reflections:
        if ref.get("question") and ref.get("answer"):
            db.session.add(ReflectionAnswer(
                session_id=session.id,
                question=ref["question"],
                answer=ref["answer"],
            ))

    db.session.commit()

    # Post-session: score, défis, badges
    score = ReflectionScoreService.calculate(user_id)
    ChallengeService.check_and_complete(user_id)
    ChallengeService.assign_daily_challenge(user_id)
    new_badges = BadgeService.check_badges(user_id)
    today = StatsService.today_stats(user_id)

    return jsonify({
        "message": "Session démarrée.",
        "session": session.to_dict(),
        "score": score,
        "today_stats": today,
        "new_badges": new_badges,
    }), 201


@sessions_bp.route("/end", methods=["POST"])
@jwt_required()
def end_session():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id requis."}), 400

    session = AISession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Session introuvable."}), 404

    if session.end_time:
        return jsonify({"message": "Session déjà terminée.", "session": session.to_dict()}), 200

    session.end_time = datetime.utcnow()
    session.duration = int((session.end_time - session.start_time).total_seconds())

    db.session.commit()

    score = ReflectionScoreService.calculate(user_id)
    ChallengeService.check_and_complete(user_id)

    return jsonify({
        "message": "Session terminée.",
        "session": session.to_dict(),
        "score": score,
    }), 200


@sessions_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    result = StatsService.session_history(user_id, page, per_page)
    return jsonify(result), 200
