"""Configuration Model"""
from app import db
from datetime import datetime

class Configuration(db.Model):
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256))
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_value(key, default=None):
        """Get configuration value by key"""
        config = Configuration.query.filter_by(key=key).first()
        return config.value if config else default

    @staticmethod
    def set_value(key, value, description=None):
        """Set configuration value"""
        config = Configuration.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
            config.updated_at = datetime.utcnow()
        else:
            config = Configuration(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()

    @staticmethod
    def is_read_only_mode():
        """Check if system is in read-only mode"""
        return Configuration.get_value('read_only_mode', 'false').lower() == 'true'

    def __repr__(self):
        return f'<Configuration {self.key}={self.value}>'