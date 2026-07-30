"""Service de statistiques."""
from datetime import datetime, timedelta

from sqlalchemy import func

from app import db
from app.models import AIPlatform, AISession, UserGoal
from app.utils.dates import today_start, week_start


class StatsService:
    @staticmethod
    def today_stats(user_id: int) -> dict:
        today = today_start()
        sessions = AISession.query.filter(
            AISession.user_id == user_id,
            AISession.start_time >= today,
        ).all()

        total_seconds = sum(s.duration or 0 for s in sessions)
        goal = UserGoal.query.filter_by(user_id=user_id).first()
        daily_limit = goal.daily_limit if goal else 120

        return {
            "sessions_today": len(sessions),
            "time_today_seconds": total_seconds,
            "time_today_minutes": round(total_seconds / 60, 1),
            "daily_limit_minutes": daily_limit,
            "goal_progress_percent": min(
                100, round((total_seconds / 60 / daily_limit) * 100, 1)
            ) if daily_limit else 0,
        }

    @staticmethod
    def dashboard_stats(user_id: int) -> dict:
        week_ago = week_start()
        today = today_start()

        # Utilisation quotidienne (7 derniers jours)
        daily_usage = []
        for i in range(6, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            total = db.session.query(
                func.coalesce(func.sum(AISession.duration), 0)
            ).filter(
                AISession.user_id == user_id,
                AISession.start_time >= day_start,
                AISession.start_time < day_end,
            ).scalar()
            daily_usage.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "label": day_start.strftime("%a"),
                "minutes": round(total / 60, 1),
                "sessions": AISession.query.filter(
                    AISession.user_id == user_id,
                    AISession.start_time >= day_start,
                    AISession.start_time < day_end,
                ).count(),
            })

        # Évolution hebdomadaire (4 semaines)
        weekly_evolution = []
        for w in range(3, -1, -1):
            w_start = week_ago - timedelta(weeks=w)
            w_end = w_start + timedelta(days=7)
            total = db.session.query(
                func.coalesce(func.sum(AISession.duration), 0)
            ).filter(
                AISession.user_id == user_id,
                AISession.start_time >= w_start,
                AISession.start_time < w_end,
            ).count()
            weekly_evolution.append({
                "week": f"S{-w}" if w else "Cette semaine",
                "sessions": total,
            })

        # Plateformes utilisées
        platform_stats = db.session.query(
            AIPlatform.name,
            func.count(AISession.id).label("count"),
            func.coalesce(func.sum(AISession.duration), 0).label("duration"),
        ).join(AISession).filter(
            AISession.user_id == user_id,
            AISession.start_time >= week_ago,
        ).group_by(AIPlatform.name).all()

        platforms = [
            {
                "name": name,
                "sessions": count,
                "minutes": round(duration / 60, 1),
            }
            for name, count, duration in platform_stats
        ]

        return {
            "daily_usage": daily_usage,
            "weekly_evolution": weekly_evolution,
            "platforms": platforms,
        }

    @staticmethod
    def session_history(user_id: int, page: int = 1, per_page: int = 20) -> dict:
        query = AISession.query.filter_by(user_id=user_id).order_by(
            AISession.start_time.desc()
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "sessions": [s.to_dict() for s in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }
