"""
Database migration script to add booking_id column to Review table
Uses SQLAlchemy methods to update database schema.
"""

from hotelweb.app import create_app
from hotelweb.extensions import db
from sqlalchemy import inspect, text

def migrate():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check existing columns in Review table
        try:
            review_columns = [col['name'] for col in inspector.get_columns('review')]
        except Exception:
            review_columns = []
        
        # Add booking_id column to Review table using SQLAlchemy
        with db.engine.connect() as conn:
            if 'booking_id' not in review_columns:
                print("Adding booking_id column to review table...")
                conn.execute(text("ALTER TABLE review ADD COLUMN booking_id INTEGER"))
                conn.commit()
                print("✓ Added booking_id column to review table")
            else:
                print("✓ booking_id column already exists in review table")
        
        print("\nMigration completed!")

if __name__ == '__main__':
    migrate()

