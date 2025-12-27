"""
Database migration script to add new profile fields and member number
"""
import sqlite3
import os
import random

DB_PATH = os.path.join("hotelweb", "instance", "hotel.db")

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting database migration for profile fields...")
    
    # Add new columns to User table
    new_columns = [
        ("member_number", "VARCHAR(20)"),
        ("phone", "VARCHAR(20)"),
        ("address", "VARCHAR(200)"),
        ("city", "VARCHAR(100)"),
        ("country", "VARCHAR(100)"),
        ("postal_code", "VARCHAR(20)"),
        ("birthday", "DATE")
    ]
    
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            print(f"✓ Added {col_name} to user table")
        except sqlite3.OperationalError as e:
            print(f"  {col_name} already exists or error: {e}")
    
    # Generate member numbers for existing users
    try:
        cursor.execute("SELECT id FROM user WHERE member_number IS NULL")
        users_without_number = cursor.fetchall()
        
        for (user_id,) in users_without_number:
            # Generate 8-digit member number
            member_number = f"{random.randint(10000000, 99999999)}"
            cursor.execute("UPDATE user SET member_number = ? WHERE id = ?", (member_number, user_id))
            print(f"✓ Generated member number for user {user_id}: {member_number}")
    except Exception as e:
        print(f"  Error generating member numbers: {e}")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed!")

if __name__ == "__main__":
    migrate_database()
