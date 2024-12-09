from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.config import Configuration
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('inventory.dashboard'))
        flash('Invalid username or password', 'error')
    
    # Check if registration is allowed for template rendering
    allow_registration = Configuration.get_setting('allow_public_registration', 'true') == 'true'
    return render_template('auth/login.html', allow_registration=allow_registration)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Check if registration is allowed
    allow_registration = Configuration.get_setting('allow_public_registration', 'true') == 'true'
    if not allow_registration:
        flash('Public registration is currently disabled', 'error')
        return redirect(url_for('auth.login'))

    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        pin = request.form.get('pin')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        new_user.set_pin(pin)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))