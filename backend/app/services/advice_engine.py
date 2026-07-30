"""Moteur de conseils personnalisés."""
from datetime import datetime, timedelta

from app.models import AISession, UserGoal
from app.utils.dates import today_start, week_start


class AdviceEngine:
    """Génère des conseils basés sur les habitudes d'utilisation."""

    @classmethod
    def get_advice(cls, user_id: int) -> list[dict]:
        advice_list = []
        week_ago = week_start()
        today = today_start()

        sessions_week = AISession.query.filter(
            AISession.user_id == user_id,
            AISession.start_time >= week_ago,
        ).all()

        if not sessions_week:
            return [{
                "type": "welcome",
                "title": "Bienvenue sur Luciole",
                "message": "Commencez par réfléchir avant chaque utilisation d'IA. "
                           "Votre score évoluera avec vos habitudes conscientes.",
                "priority": "low",
            }]

        # Sessions courtes fréquentes
        short_sessions = [s for s in sessions_week if s.duration and s.duration < 300]
        if len(short_sessions) >= 5 and len(short_sessions) / len(sessions_week) > 0.5:
            advice_list.append({
                "type": "batching",
                "title": "Regroupez vos demandes",
                "message": "Vous avez beaucoup de sessions courtes. "
                           "Essayez de regrouper vos questions en une seule session "
                           "pour réduire les allers-retours.",
                "priority": "medium",
            })

        # Utilisation nocturne
        night_sessions = [
            s for s in sessions_week
            if s.start_time.hour >= 22 or s.start_time.hour < 7
        ]
        if len(night_sessions) >= 3:
            advice_list.append({
                "type": "sleep",
                "title": "Pause nocturne recommandée",
                "message": "Vous utilisez souvent l'IA la nuit. "
                           "Une pause digitale améliore la qualité du sommeil "
                           "et la clarté de vos réflexions le lendemain.",
                "priority": "high",
            })

        # Augmentation importante
        two_weeks_ago = week_ago - timedelta(days=7)
        prev_count = AISession.query.filter(
            AISession.user_id == user_id,
            AISession.start_time >= two_weeks_ago,
            AISession.start_time < week_ago,
        ).count()
        if prev_count > 0:
            increase = (len(sessions_week) - prev_count) / prev_count
            if increase > 0.3:
                goal = UserGoal.query.filter_by(user_id=user_id).first()
                current_limit = goal.daily_limit if goal else 120
                suggested = max(30, int(current_limit * 0.9))
                advice_list.append({
                    "type": "goal",
                    "title": "Augmentation notable",
                    "message": f"Votre utilisation a augmenté de {int(increase * 100)}% cette semaine. "
                               f"Envisagez un objectif quotidien de {suggested} minutes.",
                    "priority": "high",
                    "suggested_goal": suggested,
                })

        # Réflexion insuffisante
        no_reflection = sum(1 for s in sessions_week if not s.reason or not s.needs_ai)
        if no_reflection > len(sessions_week) * 0.3:
            advice_list.append({
                "type": "reflection",
                "title": "Prenez le temps de réfléchir",
                "message": "Plusieurs sessions sans réflexion complète. "
                           "L'overlay Luciole est là pour vous aider — "
                           "répondez aux questions avant de continuer.",
                "priority": "medium",
            })

        # Utilisation consciente (needs_ai = no)
        mindful = sum(1 for s in sessions_week if s.needs_ai == "no")
        if mindful >= 3:
            advice_list.append({
                "type": "positive",
                "title": "Bravo !",
                "message": f"Vous avez identifié {mindful} fois où l'IA n'était pas nécessaire. "
                           "C'est un excellent signe de conscience numérique.",
                "priority": "low",
            })

        if not advice_list:
            advice_list.append({
                "type": "maintain",
                "title": "Continuez ainsi",
                "message": "Vos habitudes sont équilibrées. "
                           "Maintenez votre rythme de réflexion avant chaque session.",
                "priority": "low",
            })

        priority_order = {"high": 0, "medium": 1, "low": 2}
        advice_list.sort(key=lambda a: priority_order.get(a["priority"], 3))
        return advice_list
