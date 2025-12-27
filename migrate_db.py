"""
Database migration script to add new fields for loyalty and billing system
Run this script to update the database schema
"""
import sqlite3
import os

DB_PATH = os.path.join("hotelweb", "instance", "hotel.db")

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Add new columns to User table
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN lifetime_points INTEGER DEFAULT 0")
        print("✓ Added lifetime_points to user table")
    except sqlite3.OperationalError as e:
        print(f"  lifetime_points already exists or error: {e}")
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN nights_stayed INTEGER DEFAULT 0")
        print("✓ Added nights_stayed to user table")
    except sqlite3.OperationalError as e:
        print(f"  nights_stayed already exists or error: {e}")
    
    # Add new columns to Booking table
    booking_columns = [
        ("base_rate", "NUMERIC(10, 2) DEFAULT 0"),
        ("subtotal", "NUMERIC(10, 2) DEFAULT 0"),
        ("taxes", "NUMERIC(10, 2) DEFAULT 0"),
        ("fees", "NUMERIC(10, 2) DEFAULT 0"),
        ("total_cost", "NUMERIC(10, 2) DEFAULT 0"),
        ("points_earned", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_type in booking_columns:
        try:
            cursor.execute(f"ALTER TABLE booking ADD COLUMN {col_name} {col_type}")
            print(f"✓ Added {col_name} to booking table")
        except sqlite3.OperationalError as e:
            print(f"  {col_name} already exists or error: {e}")
    
    # Create PointsTransaction table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points_transaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                booking_id INTEGER,
                points INTEGER NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                description VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (booking_id) REFERENCES booking(id)
            )
        """)
        print("✓ Created points_transaction table")
    except sqlite3.OperationalError as e:
        print(f"  points_transaction table error: {e}")
    
    # Update existing users to have lifetime_points equal to current points
    try:
        cursor.execute("UPDATE user SET lifetime_points = points WHERE lifetime_points = 0 OR lifetime_points IS NULL")
        print("✓ Initialized lifetime_points for existing users")
    except Exception as e:
        print(f"  Error updating lifetime_points: {e}")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed!")

if __name__ == "__main__":
    migrate_database()
