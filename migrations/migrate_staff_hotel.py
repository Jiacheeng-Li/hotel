"""
Migration script to create staff_hotel association table
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from sqlalchemy import text, inspect

def migrate():
    app = create_app()
    with app.app_context():
        # Check if staff_hotel table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'staff_hotel' not in tables:
            print("Creating 'staff_hotel' association table...")
            try:
                # Create staff_hotel table
                db.session.execute(text("""
                    CREATE TABLE staff_hotel (
                        user_id INTEGER NOT NULL,
                        hotel_id INTEGER NOT NULL,
                        PRIMARY KEY (user_id, hotel_id),
                        FOREIGN KEY (user_id) REFERENCES user (id),
                        FOREIGN KEY (hotel_id) REFERENCES hotel (id)
                    )
                """))
                db.session.commit()
                print("✓ staff_hotel table created successfully.")
            except Exception as e:
                print(f"Error creating staff_hotel table: {e}")
                db.session.rollback()
                return
        else:
            print("✓ staff_hotel table already exists.")
        
        print("Migration complete!")

if __name__ == '__main__':
    migrate()

