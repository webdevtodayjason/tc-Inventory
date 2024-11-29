from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    pin_code = db.Column(db.String(6))  # 6-digit PIN for quick access
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_pin(self, pin):
        """Set PIN code for quick access"""
        if len(pin) != 6 or not pin.isdigit():
            raise ValueError("PIN must be 6 digits")
        self.pin_code = pin
    
    def check_pin(self, pin):
        """Verify PIN code"""
        return self.pin_code == pin

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 