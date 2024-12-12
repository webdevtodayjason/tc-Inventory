from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.config import Configuration
from app import db
from app.forms import ChangePasswordForm
from app.utils.activity_logger import log_user_activity

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    try:
        # Get configuration settings with defaults
        allow_registration = Configuration.get_setting('allow_public_registration', 'false')
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password', 'error')
                return render_template('auth/login.html', allow_registration=allow_registration)
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('inventory.dashboard'))
                
            flash('Invalid username or password', 'error')
        
        return render_template('auth/login.html', allow_registration=allow_registration)
        
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        return render_template('auth/login.html', allow_registration='false')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    try:
        # Check if registration is allowed
        allow_registration = Configuration.get_setting('allow_public_registration', 'false')
        if allow_registration.lower() != 'true':
            flash('Public registration is currently disabled', 'error')
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            pin = request.form.get('pin')
            
            if not all([username, password, email, pin]):
                flash('All fields are required', 'error')
                return render_template('auth/register.html')
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('auth/register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('auth/register.html')
            
            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            try:
                new_user.set_pin(pin)
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('auth/register.html')
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        
        return render_template('auth/register.html')
        
    except Exception as e:
        flash('An error occurred during registration', 'error')
        return redirect(url_for('auth.login'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            # Log the password change
            log_user_activity('update', current_user, {'action': 'password_change'})
            
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('inventory.dashboard'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('auth/change_password.html', form=form)