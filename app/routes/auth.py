from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from app.models.user import User
from app import db
from urllib.parse import urlparse

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    form = FlaskForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('inventory.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    form = FlaskForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=request.form['username'],
                email=request.form['email']
            )
            user.set_password(request.form['password'])
            
            # Set PIN code
            pin = request.form.get('pin')
            if not pin or len(pin) != 6 or not pin.isdigit():
                flash('PIN must be exactly 6 digits', 'danger')
                return render_template('auth/register.html', form=form)
            
            user.set_pin(pin)
            
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            current_app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('auth/register.html', form=form) 