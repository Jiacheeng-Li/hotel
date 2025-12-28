"""
Migration script to ensure all RoomType records have inventory values.
Sets default inventory to 10 if not already set.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'hotelweb')))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import RoomType

app = create_app()

def migrate():
    with app.app_context():
        print("Checking RoomType inventory values...")
        
        # Get all room types without inventory or with inventory = 0
        room_types = RoomType.query.filter(
            (RoomType.inventory == None) | (RoomType.inventory == 0)
        ).all()
        
        if room_types:
            print(f"Found {len(room_types)} room types without inventory. Setting default to 10...")
            for rt in room_types:
                rt.inventory = 10
                print(f"  - Set inventory for {rt.name} (ID: {rt.id}) to 10")
            
            db.session.commit()
            print("Migration completed successfully!")
        else:
            print("All room types already have inventory values.")
        
        # Display summary
        total = RoomType.query.count()
        print(f"\nTotal room types: {total}")
        for rt in RoomType.query.all():
            print(f"  - {rt.name} (Hotel: {rt.hotel.name}): inventory = {rt.inventory}")

if __name__ == '__main__':
    migrate()

