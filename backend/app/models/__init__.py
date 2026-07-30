"""Modèles SQLAlchemy."""
from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    sessions = db.relationship("AISession", back_populates="user", lazy="dynamic")
    goal = db.relationship("UserGoal", back_populates="user", uselist=False)
    scores = db.relationship("Score", back_populates="user", lazy="dynamic")
    user_challenges = db.relationship("UserChallenge", back_populates="user", lazy="dynamic")
    user_badges = db.relationship("UserBadge", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }


class AIPlatform(db.Model):
    __tablename__ = "ai_platforms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    url = db.Column(db.String(255), nullable=False)

    sessions = db.relationship("AISession", back_populates="platform", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "url": self.url}


class AISession(db.Model):
    __tablename__ = "ai_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey("ai_platforms.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    reason = db.Column(db.String(50), nullable=True)
    needs_ai = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="sessions")
    platform = db.relationship("AIPlatform", back_populates="sessions")
    reflection_answers = db.relationship(
        "ReflectionAnswer", back_populates="session", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform.name if self.platform else None,
            "platform_id": self.platform_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "duration_minutes": round(self.duration / 60, 1) if self.duration else None,
            "reason": self.reason,
            "needs_ai": self.needs_ai,
        }


class UserGoal(db.Model):
    __tablename__ = "user_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    daily_limit = db.Column(db.Integer, nullable=False, default=120)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = db.relationship("User", back_populates="goal")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "daily_limit": self.daily_limit,
            "daily_limit_hours": round(self.daily_limit / 60, 1),
        }


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    reward = db.Column(db.Integer, nullable=False, default=10)
    active = db.Column(db.Boolean, nullable=False, default=True)

    user_challenges = db.relationship("UserChallenge", back_populates="challenge", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "reward": self.reward,
            "active": self.active,
        }


class UserChallenge(db.Model):
    __tablename__ = "user_challenges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="user_challenges")
    challenge = db.relationship("Challenge", back_populates="user_challenges")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "challenge": self.challenge.to_dict() if self.challenge else None,
            "completed": self.completed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=True)

    user_badges = db.relationship("UserBadge", back_populates="badge", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
        }


class UserBadge(db.Model):
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="user_badges")
    badge = db.relationship("Badge", back_populates="user_badges")

    def to_dict(self):
        return {
            "id": self.id,
            "badge": self.badge.to_dict() if self.badge else None,
            "earned_at": self.earned_at.isoformat(),
        }


class ReflectionAnswer(db.Model):
    __tablename__ = "reflection_answers"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("ai_sessions.id"), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    session = db.relationship("AISession", back_populates="reflection_answers")

    def to_dict(self):
        return {"id": self.id, "question": self.question, "answer": self.answer}


class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    level = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="scores")

    def to_dict(self):
        return {
            "id": self.id,
            "value": round(self.value, 1),
            "level": self.level,
            "created_at": self.created_at.isoformat(),
        }
