"""Routes du dashboard web (pages HTML)."""
from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("index.html")


@dashboard_bp.route("/login")
def login_page():
    return render_template("login.html")


@dashboard_bp.route("/register")
def register_page():
    return render_template("register.html")


@dashboard_bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@dashboard_bp.route("/profile")
def profile_page():
    return render_template("profile.html")


@dashboard_bp.route("/challenges")
def challenges_page():
    return render_template("challenges.html")


@dashboard_bp.route("/history")
def history_page():
    return render_template("history.html")
