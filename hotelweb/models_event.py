from datetime import datetime
from .extensions import db

class UserEvent(db.Model):
    """Track special user events like birthdays and holidays"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'birthday', 'new_year'
    event_year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    reward_type = db.Column(db.String(20))  # 'points', 'breakfast'
    reward_amount = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='events', lazy=True)

