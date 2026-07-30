"""Service de gamification — défis et badges."""
from datetime import datetime, timedelta

from app import db
from app.models import AISession, Badge, Challenge, UserBadge, UserChallenge
from app.services.reflection_score_service import ReflectionScoreService
from app.utils.dates import today_start, week_start


class ChallengeService:
    """Gestion des défis utilisateur."""

    @staticmethod
    def get_active_challenges(user_id: int) -> list:
        challenges = Challenge.query.filter_by(active=True).all()
        result = []
        for challenge in challenges:
            uc = UserChallenge.query.filter_by(
                user_id=user_id, challenge_id=challenge.id
            ).first()
            result.append({
                **challenge.to_dict(),
                "user_progress": uc.to_dict() if uc else None,
                "completed": uc.completed if uc else False,
            })
        return result

    @staticmethod
    def assign_daily_challenge(user_id: int) -> dict | None:
        """Assigne un défi quotidien non complété."""
        daily = Challenge.query.filter_by(type="daily", active=True).first()
        if not daily:
            return None

        existing = UserChallenge.query.filter_by(
            user_id=user_id, challenge_id=daily.id
        ).first()

        if existing:
            # Réinitialiser si défi d'hier
            if existing.started_at.date() < datetime.utcnow().date() and existing.completed:
                existing.completed = False
                existing.started_at = datetime.utcnow()
                existing.completed_at = None
                db.session.commit()
            return existing.to_dict()

        uc = UserChallenge(user_id=user_id, challenge_id=daily.id)
        db.session.add(uc)
        db.session.commit()
        return uc.to_dict()

    @classmethod
    def check_and_complete(cls, user_id: int) -> list:
        """Vérifie et complète les défis en cours."""
        completed = []
        user_challenges = UserChallenge.query.filter_by(
            user_id=user_id, completed=False
        ).all()

        for uc in user_challenges:
            challenge = uc.challenge
            if not challenge:
                continue

            if challenge.title == "Réflexion 24h":
                today = today_start()
                sessions = AISession.query.filter(
                    AISession.user_id == user_id,
                    AISession.start_time >= today,
                ).all()
                if sessions and all(s.reason and s.needs_ai for s in sessions):
                    if len(sessions) >= 1:
                        uc.completed = True
                        uc.completed_at = datetime.utcnow()
                        completed.append(challenge.title)

            elif challenge.title == "Réduction 10%":
                yesterday_start = today_start() - timedelta(days=1)
                yesterday_end = today_start()
                today = today_start()

                yesterday_dur = db.session.query(
                    db.func.coalesce(db.func.sum(AISession.duration), 0)
                ).filter(
                    AISession.user_id == user_id,
                    AISession.start_time >= yesterday_start,
                    AISession.start_time < yesterday_end,
                ).scalar()

                today_dur = db.session.query(
                    db.func.coalesce(db.func.sum(AISession.duration), 0)
                ).filter(
                    AISession.user_id == user_id,
                    AISession.start_time >= today,
                ).scalar()

                if yesterday_dur > 0 and today_dur <= yesterday_dur * 0.9:
                    uc.completed = True
                    uc.completed_at = datetime.utcnow()
                    completed.append(challenge.title)

        if completed:
            db.session.commit()
        return completed


class BadgeService:
    """Attribution automatique des badges."""

    @classmethod
    def check_badges(cls, user_id: int) -> list:
        earned = []
        existing_ids = {
            ub.badge_id
            for ub in UserBadge.query.filter_by(user_id=user_id).all()
        }

        badges = Badge.query.all()
        badge_map = {b.name: b for b in badges}

        session_count = AISession.query.filter_by(user_id=user_id).count()
        if "Premier pas" in badge_map and badge_map["Premier pas"].id not in existing_ids:
            reflected = AISession.query.filter(
                AISession.user_id == user_id,
                AISession.reason.isnot(None),
            ).count()
            if reflected >= 1:
                cls._award(user_id, badge_map["Premier pas"].id)
                earned.append("Premier pas")

        # 3 jours conscients
        if "3 jours conscients" in badge_map and badge_map["3 jours conscients"].id not in existing_ids:
            if cls._consecutive_days_above_score(user_id, 40, 3):
                cls._award(user_id, badge_map["3 jours conscients"].id)
                earned.append("3 jours conscients")

        # Une semaine maîtrisée
        if "Une semaine maîtrisée" in badge_map and badge_map["Une semaine maîtrisée"].id not in existing_ids:
            if cls._consecutive_days_above_score(user_id, 60, 7):
                cls._award(user_id, badge_map["Une semaine maîtrisée"].id)
                earned.append("Une semaine maîtrisée")

        # Utilisateur réfléchi
        if "Utilisateur réfléchi" in badge_map and badge_map["Utilisateur réfléchi"].id not in existing_ids:
            if cls._consecutive_days_above_score(user_id, 80, 5):
                cls._award(user_id, badge_map["Utilisateur réfléchi"].id)
                earned.append("Utilisateur réfléchi")

        # Réduction 50%
        if "Réduction 50%" in badge_map and badge_map["Réduction 50%"].id not in existing_ids:
            if cls._week_reduction(user_id, 0.5):
                cls._award(user_id, badge_map["Réduction 50%"].id)
                earned.append("Réduction 50%")

        if earned:
            db.session.commit()
        return earned

    @staticmethod
    def _award(user_id: int, badge_id: int):
        ub = UserBadge(user_id=user_id, badge_id=badge_id)
        db.session.add(ub)

    @staticmethod
    def _consecutive_days_above_score(user_id: int, threshold: float, days: int) -> bool:
        from app.models import Score

        for i in range(days):
            day_start = today_start() - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            score = (
                Score.query.filter(
                    Score.user_id == user_id,
                    Score.created_at >= day_start,
                    Score.created_at < day_end,
                )
                .order_by(Score.created_at.desc())
                .first()
            )
            if not score or score.value < threshold:
                return False
        return True

    @staticmethod
    def _week_reduction(user_id: int, ratio: float) -> bool:
        week_ago = week_start()
        two_weeks = week_ago - timedelta(days=7)

        prev = db.session.query(
            db.func.coalesce(db.func.sum(AISession.duration), 0)
        ).filter(
            AISession.user_id == user_id,
            AISession.start_time >= two_weeks,
            AISession.start_time < week_ago,
        ).scalar()

        curr = db.session.query(
            db.func.coalesce(db.func.sum(AISession.duration), 0)
        ).filter(
            AISession.user_id == user_id,
            AISession.start_time >= week_ago,
        ).scalar()

        return prev > 0 and curr <= prev * (1 - ratio)

    @staticmethod
    def get_user_badges(user_id: int) -> list:
        badges = UserBadge.query.filter_by(user_id=user_id).order_by(
            UserBadge.earned_at.desc()
        ).all()
        return [b.to_dict() for b in badges]
