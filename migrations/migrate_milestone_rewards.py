"""
Database migration script to add Milestone Rewards and Breakfast/Points Payment features
Uses SQLAlchemy methods to update database schema.
"""

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import Booking, MilestoneReward
from sqlalchemy import inspect, text

def migrate():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check existing columns in Booking table
        try:
            booking_columns = [col['name'] for col in inspector.get_columns('booking')]
        except Exception:
            booking_columns = []
        
        # Add new columns to Booking table using SQLAlchemy
        columns_added = []
        with db.engine.connect() as conn:
            if 'breakfast_included' not in booking_columns:
                conn.execute(text("ALTER TABLE booking ADD COLUMN breakfast_included BOOLEAN DEFAULT FALSE"))
                columns_added.append('breakfast_included')
            if 'breakfast_price_per_room' not in booking_columns:
                conn.execute(text("ALTER TABLE booking ADD COLUMN breakfast_price_per_room NUMERIC(10, 2) DEFAULT 0"))
                columns_added.append('breakfast_price_per_room')
            if 'points_used' not in booking_columns:
                conn.execute(text("ALTER TABLE booking ADD COLUMN points_used INTEGER DEFAULT 0"))
                columns_added.append('points_used')
            if 'payment_method' not in booking_columns:
                conn.execute(text("ALTER TABLE booking ADD COLUMN payment_method VARCHAR(20) DEFAULT 'pay_now'"))
                columns_added.append('payment_method')
            conn.commit()
        
        if columns_added:
            print(f"✓ Added columns to Booking table: {', '.join(columns_added)}")
        else:
            print("✓ Booking table already has all required columns")
        
        # Create MilestoneReward table using SQLAlchemy
        milestone_table_exists = db.engine.dialect.has_table(db.engine.connect(), 'milestone_reward')
        if not milestone_table_exists:
            # Use SQLAlchemy to create the table from the model
            MilestoneReward.__table__.create(db.engine, checkfirst=True)
            print("✓ Created MilestoneReward table")
        else:
            print("✓ MilestoneReward table already exists")
        
        print("\n✓ Migration completed successfully!")

if __name__ == '__main__':
    migrate()

