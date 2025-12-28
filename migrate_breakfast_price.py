"""
Database migration script to add breakfast_price to Hotel model and update existing hotels
Also ensures all hotels have Breakfast amenity
"""

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import Hotel, Amenity, RoomType
from sqlalchemy import inspect, text

def migrate():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check existing columns in Hotel table
        try:
            hotel_columns = [col['name'] for col in inspector.get_columns('hotel')]
        except Exception:
            hotel_columns = []
        
        # Add breakfast_price column if it doesn't exist
        with db.engine.connect() as conn:
            if 'breakfast_price' not in hotel_columns:
                conn.execute(text("ALTER TABLE hotel ADD COLUMN breakfast_price NUMERIC(10, 2) DEFAULT 25.00"))
                conn.commit()
                print("✓ Added breakfast_price column to Hotel table")
            else:
                print("✓ breakfast_price column already exists")
        
        # Update all hotels with breakfast_price based on star rating
        hotels = Hotel.query.all()
        breakfast_price_map = {5: 50.00, 4: 40.00, 3: 30.00, 2: 20.00, 1: 10.00}
        updated_count = 0
        
        for hotel in hotels:
            expected_price = breakfast_price_map.get(hotel.stars, 25.00)
            if hotel.breakfast_price != expected_price:
                hotel.breakfast_price = expected_price
                updated_count += 1
        
        # Ensure Breakfast amenity exists
        breakfast_amenity = Amenity.query.filter_by(name='Breakfast').first()
        if not breakfast_amenity:
            breakfast_amenity = Amenity(name='Breakfast')
            db.session.add(breakfast_amenity)
            db.session.commit()
            print("✓ Created Breakfast amenity")
        else:
            print("✓ Breakfast amenity already exists")
        
        # Ensure all room types have Breakfast amenity
        room_types = RoomType.query.all()
        breakfast_added_count = 0
        
        for rt in room_types:
            if breakfast_amenity not in rt.amenities:
                rt.amenities.append(breakfast_amenity)
                breakfast_added_count += 1
        
        db.session.commit()
        
        print(f"✓ Updated {updated_count} hotels with breakfast prices based on star ratings")
        print(f"✓ Added Breakfast amenity to {breakfast_added_count} room types")
        print("✓ Migration completed successfully!")

if __name__ == '__main__':
    migrate()

