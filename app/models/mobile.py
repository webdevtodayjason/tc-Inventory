"""Mobile API Models"""
from app import db
from datetime import datetime

class MobileCheckoutReason(db.Model):
    """Model for mobile checkout reasons"""
    __tablename__ = 'mobile_checkout_reasons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CheckoutReason {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        }

# Add initial data
def init_checkout_reasons():
    """Initialize checkout reasons if they don't exist"""
    reasons = [
        {
            'name': 'CLIENT INSTALL',
            'description': 'Installation at client site',
            'is_active': True
        },
        {
            'name': 'TESTING',
            'description': 'Testing or validation',
            'is_active': True
        },
        {
            'name': 'REPAIR',
            'description': 'Repair or maintenance',
            'is_active': True
        },
        {
            'name': 'DEMO',
            'description': 'Product demonstration',
            'is_active': True
        }
    ]

    for reason_data in reasons:
        reason = MobileCheckoutReason.query.filter_by(name=reason_data['name']).first()
        if not reason:
            reason = MobileCheckoutReason(**reason_data)
            db.session.add(reason)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing checkout reasons: {str(e)}")

class MobileDeviceToken(db.Model):
    """Model for mobile device tokens (for push notifications)"""
    __tablename__ = 'mobile_device_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_token = db.Column(db.String(255), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # 'ios' or 'android'
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('device_tokens', lazy=True))

    def __repr__(self):
        return f'<MobileDeviceToken {self.device_type}:{self.user_id}>' 