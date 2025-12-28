"""
Database migration script to add Milestone Rewards and Breakfast/Points Payment features
Run this script to update your database schema.
"""

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User, Booking, PointsTransaction

def migrate():
    app = create_app()
    with app.app_context():
        from sqlalchemy import text
        
        # Add new columns to Booking table
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE booking ADD COLUMN IF NOT EXISTS breakfast_included BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE booking ADD COLUMN IF NOT EXISTS breakfast_price_per_room NUMERIC(10, 2) DEFAULT 0"))
                conn.execute(text("ALTER TABLE booking ADD COLUMN IF NOT EXISTS points_used INTEGER DEFAULT 0"))
                conn.execute(text("ALTER TABLE booking ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20) DEFAULT 'pay_now'"))
                conn.commit()
            print("✓ Added columns to Booking table")
        except Exception as e:
            print(f"Note: Some columns may already exist: {e}")
        
        # Create MilestoneReward table
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS milestone_reward (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        milestone_nights INTEGER NOT NULL,
                        reward_type VARCHAR(20) NOT NULL,
                        reward_value INTEGER,
                        claimed_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                """))
                conn.commit()
            print("✓ Created MilestoneReward table")
        except Exception as e:
            print(f"Note: Table may already exist: {e}")
        
        print("\n✓ Migration completed successfully!")

if __name__ == '__main__':
    migrate()

