"""
Migration script to add favorite_hotel table
"""
from extensions import db
from models import FavoriteHotel
from app import create_app

app = create_app()

with app.app_context():
    try:
        # Create the table
        db.create_all()
        print("✓ favorite_hotel table created successfully")
    except Exception as e:
        print(f"✗ Error creating favorite_hotel table: {e}")

