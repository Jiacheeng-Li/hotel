"""
Migration script to add role field to User model
Run this once to update existing users to have 'customer' role
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        # Check if role column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'role' not in columns:
            print("Adding 'role' column to user table...")
            try:
                # Add role column with default value 'customer'
                db.session.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'customer'"))
                db.session.commit()
                print("✓ Role column added successfully.")
            except Exception as e:
                print(f"Error adding role column: {e}")
                db.session.rollback()
                return
        
        # Update all existing users to have 'customer' role if they don't have one
        users = User.query.all()
        updated = 0
        for user in users:
            if not hasattr(user, 'role') or user.role is None or user.role == '':
                user.role = 'customer'
                updated += 1
        
        db.session.commit()
        print(f"✓ Migration complete! Updated {updated} users with 'customer' role.")
        print(f"Total users in database: {len(users)}")

if __name__ == '__main__':
    migrate()

