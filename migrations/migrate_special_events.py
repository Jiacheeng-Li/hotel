import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from hotelweb.app import create_app
from hotelweb.extensions import db

app = create_app()

def migrate():
    with app.app_context():
        print("Starting migration...")
        
        # 1. Create UserEvent table
        # We can use db.create_all() which will create UserEvent because it's new
        # and won't touch existing tables
        print("Creating new tables...")
        db.create_all()
        
        # 2. Add columns to MilestoneReward table
        # source, description
        print("Updating MilestoneReward table...")
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE milestone_reward ADD COLUMN source VARCHAR(50) DEFAULT 'milestone'"))
                print("Added 'source' column.")
            except Exception as e:
                print(f"Column 'source' might already exist: {e}")
                
            try:
                conn.execute(text("ALTER TABLE milestone_reward ADD COLUMN description VARCHAR(200)"))
                print("Added 'description' column.")
            except Exception as e:
                print(f"Column 'description' might already exist: {e}")
                
            conn.commit()
            
        print("Migration completed.")

if __name__ == '__main__':
    migrate()

