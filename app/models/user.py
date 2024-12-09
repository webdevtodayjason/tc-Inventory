from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    pin = db.Column(db.String(6))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    def set_password(self, password):
        """Hash password using bcrypt"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password):
        """Verify password using bcrypt"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"Password check error: {e}")
            return False
    
    def set_pin(self, pin):
        """Set PIN code for quick access"""
        if len(pin) != 6 or not pin.isdigit():
            raise ValueError("PIN must be 6 digits")
        self.pin = pin
    
    def check_pin(self, pin):
        """Verify PIN code"""
        return self.pin == pin

    @property
    def role(self):
        """Return user role based on is_admin flag"""
        return 'admin' if self.is_admin else 'user'

    @role.setter
    def role(self, value):
        """Set is_admin based on role value"""
        self.is_admin = (value == 'admin')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 