"""Service de calcul du score de réflexion (0-100)."""
from datetime import datetime, timedelta

from sqlalchemy import func

from app import db
from app.models import AISession, Score, UserGoal
from app.utils.dates import today_start, week_start


SCORE_LEVELS = [
    (0, 20, "Utilisation automatique"),
    (21, 40, "Utilisation réactive"),
    (41, 60, "Utilisation consciente"),
    (61, 80, "Utilisation réfléchie"),
    (81, 100, "Utilisation maîtrisée"),
]


class ReflectionScoreService:
    """Calcule un score de réflexion basé sur les habitudes d'utilisation."""

    @staticmethod
    def get_level(score: float) -> str:
        for low, high, label in SCORE_LEVELS:
            if low <= score <= high:
                return label
        return SCORE_LEVELS[-1][2]

    @classmethod
    def calculate(cls, user_id: int) -> dict:
        now = datetime.utcnow()
        week_ago = week_start()
        today = today_start()

        sessions_week = AISession.query.filter(
            AISession.user_id == user_id,
            AISession.start_time >= week_ago,
        ).all()

        sessions_today = [s for s in sessions_week if s.start_time >= today]

        if not sessions_week:
            return cls._save_score(user_id, 50.0)

        # 1. Fréquence (moins de sessions = mieux, max 7/jour acceptable)
        avg_daily_sessions = len(sessions_week) / 7
        frequency_score = max(0, 100 - (avg_daily_sessions - 3) * 15) if avg_daily_sessions > 3 else 100

        # 2. Durée moyenne (sessions courtes = mieux pour réflexion)
        durations = [s.duration for s in sessions_week if s.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0
        # Optimal: 5-20 min (300-1200 sec)
        if avg_duration <= 1200:
            duration_score = 100 - max(0, (avg_duration - 300) / 9)
        else:
            duration_score = max(0, 100 - (avg_duration - 1200) / 60)

        # 3. Réflexions complètes (reason + needs_ai renseignés)
        reflected = sum(1 for s in sessions_week if s.reason and s.needs_ai)
        reflection_rate = reflected / len(sessions_week)
        reflection_score = reflection_rate * 100

        # 4. Respect des objectifs
        goal = UserGoal.query.filter_by(user_id=user_id).first()
        daily_limit_min = goal.daily_limit if goal else 120
        today_minutes = sum((s.duration or 0) for s in sessions_today) / 60
        if today_minutes <= daily_limit_min:
            goal_score = 100
        else:
            over_ratio = (today_minutes - daily_limit_min) / daily_limit_min
            goal_score = max(0, 100 - over_ratio * 100)

        # 5. Évolution (comparer semaine courante vs précédente)
        two_weeks_ago = week_ago - timedelta(days=7)
        prev_sessions = AISession.query.filter(
            AISession.user_id == user_id,
            AISession.start_time >= two_weeks_ago,
            AISession.start_time < week_ago,
        ).count()
        if prev_sessions == 0:
            evolution_score = 70
        else:
            change = (len(sessions_week) - prev_sessions) / prev_sessions
            if change <= 0:
                evolution_score = min(100, 80 + abs(change) * 40)
            else:
                evolution_score = max(0, 80 - change * 60)

        # Bonus: réponses "needs_ai" = no ou partially
        mindful = sum(1 for s in sessions_week if s.needs_ai in ("no", "partially"))
        mindful_bonus = (mindful / len(sessions_week)) * 10

        weights = {
            "frequency": 0.15,
            "duration": 0.20,
            "reflection": 0.30,
            "goal": 0.20,
            "evolution": 0.15,
        }

        raw_score = (
            frequency_score * weights["frequency"]
            + duration_score * weights["duration"]
            + reflection_score * weights["reflection"]
            + goal_score * weights["goal"]
            + evolution_score * weights["evolution"]
            + mindful_bonus
        )
        final_score = max(0, min(100, raw_score))

        return cls._save_score(user_id, final_score)

    @classmethod
    def _save_score(cls, user_id: int, value: float) -> dict:
        level = cls.get_level(value)
        score = Score(user_id=user_id, value=value, level=level)
        db.session.add(score)
        db.session.commit()
        return score.to_dict()

    @staticmethod
    def get_latest(user_id: int) -> dict | None:
        score = (
            Score.query.filter_by(user_id=user_id)
            .order_by(Score.created_at.desc())
            .first()
        )
        return score.to_dict() if score else None

    @staticmethod
    def get_history(user_id: int, days: int = 30) -> list:
        since = datetime.utcnow() - timedelta(days=days)
        scores = (
            Score.query.filter(Score.user_id == user_id, Score.created_at >= since)
            .order_by(Score.created_at.asc())
            .all()
        )
        return [s.to_dict() for s in scores]
