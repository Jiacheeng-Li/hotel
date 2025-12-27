import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    
    # Database
    # Priority: DATABASE_URL (for prod/PypthonAnywhere) > SQLite local
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'hotel.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
