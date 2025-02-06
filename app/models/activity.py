from app import db
from datetime import datetime

class Activity(db.Model):
    """Model for storing activity logs"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    item_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    details = db.Column(db.JSON)
    item_identifier = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='activities')

    def __repr__(self):
        return f'<Activity {self.action} {self.item_type} {self.item_identifier}>' 