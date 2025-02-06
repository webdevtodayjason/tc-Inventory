"""Decorators for the application"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models.config import Configuration

def admin_required(f):
    """Require admin role for a view"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You must be an administrator to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def check_read_only(f):
    """Check if system is in read-only mode"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if Configuration.is_read_only_mode() and request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            flash('System is currently in read-only mode. Create, edit, and delete operations are disabled.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function 