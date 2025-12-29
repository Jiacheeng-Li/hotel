#!/usr/bin/env python3
"""
Migration script to add tier retention fields to User model.
Adds: tier_earned_date, tier_expiry_date, current_year_nights, current_year_points
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from datetime import date, timedelta

def migrate_tier_retention():
    """Add tier retention columns to user table"""
    app = create_app()
    
    with app.app_context():
        print("Starting tier retention migration...")
        
        try:
            # Add new columns using raw SQL (SQLite compatible)
            with db.engine.connect() as conn:
                # Check if columns already exist
                result = conn.execute(db.text("PRAGMA table_info(user)"))
                columns = [row[1] for row in result]
                
                if 'tier_earned_date' not in columns:
                    print("Adding tier_earned_date column...")
                    conn.execute(db.text("ALTER TABLE user ADD COLUMN tier_earned_date DATE"))
                    conn.commit()
                    print("✓ Added tier_earned_date")
                else:
                    print("✓ tier_earned_date already exists")
                
                if 'tier_expiry_date' not in columns:
                    print("Adding tier_expiry_date column...")
                    conn.execute(db.text("ALTER TABLE user ADD COLUMN tier_expiry_date DATE"))
                    conn.commit()
                    print("✓ Added tier_expiry_date")
                else:
                    print("✓ tier_expiry_date already exists")
                
                if 'current_year_nights' not in columns:
                    print("Adding current_year_nights column...")
                    conn.execute(db.text("ALTER TABLE user ADD COLUMN current_year_nights INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✓ Added current_year_nights")
                else:
                    print("✓ current_year_nights already exists")
                
                if 'current_year_points' not in columns:
                    print("Adding current_year_points column...")
                    conn.execute(db.text("ALTER TABLE user ADD COLUMN current_year_points INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✓ Added current_year_points")
                else:
                    print("✓ current_year_points already exists")
            
            # Initialize tier dates for existing users
            from hotelweb.models import User
            users = User.query.all()
            print(f"\nInitializing tier dates for {len(users)} users...")
            
            for user in users:
                if not user.tier_earned_date:
                    user.tier_earned_date = date.today()
                    user.tier_expiry_date = date.today() + timedelta(days=365)
                    print(f"  Set tier dates for {user.username}")
            
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_tier_retention()

