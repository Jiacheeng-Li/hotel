"""
Database migration script to add breakfast voucher tracking fields
Uses SQLAlchemy methods to update database schema.
"""

from hotelweb.app import create_app
from hotelweb.extensions import db
from sqlalchemy import inspect, text

def migrate():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check existing columns in MilestoneReward table
        try:
            milestone_columns = [col['name'] for col in inspector.get_columns('milestone_reward')]
        except Exception:
            milestone_columns = []
        
        # Check existing columns in Booking table
        try:
            booking_columns = [col['name'] for col in inspector.get_columns('booking')]
        except Exception:
            booking_columns = []
        
        columns_added = []
        with db.engine.connect() as conn:
            # Add breakfasts_used to MilestoneReward
            if 'breakfasts_used' not in milestone_columns:
                conn.execute(text("ALTER TABLE milestone_reward ADD COLUMN breakfasts_used INTEGER DEFAULT 0"))
                columns_added.append('milestone_reward.breakfasts_used')
            
            # Add breakfast_voucher_used to Booking
            if 'breakfast_voucher_used' not in booking_columns:
                conn.execute(text("ALTER TABLE booking ADD COLUMN breakfast_voucher_used INTEGER"))
                # Add foreign key constraint if possible (SQLite may not support this)
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_booking_breakfast_voucher 
                        ON booking(breakfast_voucher_used)
                    """))
                except Exception:
                    pass  # Index creation may fail, but that's okay
                columns_added.append('booking.breakfast_voucher_used')
            
            conn.commit()
        
        if columns_added:
            print(f"✓ Added columns: {', '.join(columns_added)}")
        else:
            print("✓ All required columns already exist")
        
        print("✓ Migration completed successfully!")

if __name__ == '__main__':
    migrate()

