from flask import Blueprint
from app import db
from sqlalchemy import text

bp = Blueprint('system', __name__)

@bp.route("/dbcheck")
def dbcheck():
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        if result == 1:
            return "DB connection OK"
        return "No Result"
    except Exception as e:
        return f"DB connection failed: {e}"

@bp.route("/health")
def health():
    """Basic health check endpoint"""
    return "OK" 