from app import db

class Configuration(db.Model):
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    @classmethod
    def get_setting(cls, key, default=None):
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default

    def __repr__(self):
        return f'<Configuration {self.key}>'