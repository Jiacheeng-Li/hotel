"""
Database migration script to create ContactMessage table
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import ContactMessage

def migrate():
    app = create_app()
    with app.app_context():
        print("Checking for 'contact_message' table...")
        inspector = inspect(db.engine)
        if not inspector.has_table('contact_message'):
            ContactMessage.__table__.create(db.engine)
            print("✓ 'contact_message' table created successfully.")
        else:
            print("✓ 'contact_message' table already exists.")
        db.session.commit()
        print("Migration complete!")

if __name__ == '__main__':
    migrate()

