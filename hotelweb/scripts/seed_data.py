import sys
import os
import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User, Hotel, RoomType, Amenity, Booking, Brand, Review

app = create_app()

def seed():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()

        print("Seeding Brands...")
        brands_data = [
            {"name": "Grand Apex", "description": "Timeless luxury and impeccable service for the discerning traveler.", "logo_color": "#b45309"},
            {"name": "Urban Pulse", "description": "Chic, modern hotels located in the heartbeat of the world's most exciting cities.", "logo_color": "#1e40af"},
            {"name": "Family Haven", "description": "Spacious resorts designed for family fun and relaxation.", "logo_color": "#047857"},
            {"name": "Metro Express", "description": "Smart, efficient, and affordable comfort for the busy traveler.", "logo_color": "#b91c1c"}
        ]
        
        brands = {}
        for b_data in brands_data:
            brand = Brand(name=b_data["name"], description=b_data["description"], logo_color=b_data["logo_color"])
            db.session.add(brand)
            brands[b_data["name"]] = brand
        
        db.session.commit()

        print("Seeding Amenities...")
        amenity_names = [
            "Free Wi-Fi", "Swimming Pool", "Gym", "Spa", "Restaurant", "Bar", 
            "Room Service", "Parking", "Airport Shuttle", "Pet Friendly", 
            "Conference Room", "Kids Club", "Ocean View", "Smart TV", "Mini Bar", "Rooftop Terrace", "Yoga Studio"
        ]
        amenities = {}
        for name in amenity_names:
            am = Amenity(name=name)
            db.session.add(am)
            amenities[name] = am
        db.session.commit()

        print("Generating Massive Hotel Data...")
        
        cities = [
            {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "London", "lat": 51.5074, "lon": -0.1278},
            {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
            {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
            {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
            {"name": "Dubai", "lat": 25.2048, "lon": 55.2708},
            {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
            {"name": "Rome", "lat": 41.9028, "lon": 12.4964},
            {"name": "Barcelona", "lat": 41.3851, "lon": 2.1734},
            {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
            {"name": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
            {"name": "Berlin", "lat": 52.5200, "lon": 13.4050}
        ]

        # Pool of images for variety
        images_pool = {
            "Grand Apex": [
                "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=800&q=80"
            ],
            "Urban Pulse": [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=800&q=80"
            ],
            "Family Haven": [
                "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-6e635aa13971?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=800&q=80"
            ],
            "Metro Express": [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1625244724120-1fd1d34d00f6?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1524936964167-d8679f40076a?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80"
            ]
        }

        # Suffixes for hotel names to create variety
        suffixes = {
            "Grand Apex": ["Palace", "Tower", "Riverside", "Gardens", "Plaza", "Grand", "Reserve"],
            "Urban Pulse": ["Downtown", "City Center", "Arts District", "Port", "Hub", "Central", "Loft"],
            "Family Haven": ["Resort", "Park", "Beachside", "Lagoon", "Villas", "Club", "Oasis"],
            "Metro Express": ["Station", "Airport", "Central", "North", "South", "City", "Market"]
        }

        created_hotels = []

        for city_info in cities:
            city_name = city_info["name"]
            base_lat = city_info["lat"]
            base_lon = city_info["lon"]

            # For each city, generate 1 or 2 hotels per brand
            for brand_name, brand_obj in brands.items():
                num_hotels = random.choice([1, 1, 2]) # Mostly 1 or 2
                
                for i in range(num_hotels):
                    suffix = random.choice(suffixes[brand_name])
                    
                    # Ensure unique names if we pick same suffix (simple retry logic or append number)
                    # For simplicity, we just construct name. 
                    # If multiple hotels of same brand in same city, we force different suffixes by shuffling?
                    # Let's just pick random.
                    
                    hotel_name = f"{brand_name} {city_name} {suffix}"
                    if any(h.name == hotel_name for h in created_hotels):
                        hotel_name = f"{brand_name} {city_name} {suffix} II"

                    # Random offset for lat/lon to spread them out on map
                    lat_offset = (random.random() - 0.5) * 0.1 # approx 10km spread
                    lon_offset = (random.random() - 0.5) * 0.1

                    # Star rating variance
                    base_stars = {
                        "Grand Apex": 5,
                        "Urban Pulse": 4,
                        "Family Haven": 4,
                        "Metro Express": 3
                    }[brand_name]
                    
                    # 10% chance to have +/- 1 star
                    stars = base_stars
                    if random.random() > 0.9:
                        stars = max(1, min(5, stars + random.choice([-1, 1])))

                    hotel = Hotel(
                        name=hotel_name,
                        city=city_name,
                        address=f"{random.randint(1, 999)} {city_name} Ave",
                        description=f"Experience the unique charm of {city_name} with {brand_name}'s signature hospitality.",
                        stars=stars,
                        image_url=random.choice(images_pool[brand_name]),
                        latitude=base_lat + lat_offset,
                        longitude=base_lon + lon_offset,
                        brand=brand_obj
                    )
                    db.session.add(hotel)
                    created_hotels.append(hotel)

                    # Create Room Types
                    # Define templates locally or reuse
                    rt_templates = [
                        {"name": "Standard Room", "price_base": 100, "cap": 2},
                        {"name": "Deluxe Room", "price_base": 150, "cap": 2},
                        {"name": "Family Suite", "price_base": 250, "cap": 4},
                        {"name": "Executive Suite", "price_base": 400, "cap": 2},
                        {"name": "Penthouse", "price_base": 1000, "cap": 4}
                    ]
                    
                    # Filter templates by brand tier
                    if brand_name == "Grand Apex":
                        brand_rts = rt_templates[1:] # No Standard
                        price_mult = 2.0
                    elif brand_name == "Metro Express":
                        brand_rts = rt_templates[:2] # Only Std/Deluxe
                        price_mult = 0.8
                    else:
                        brand_rts = rt_templates[:4]
                        price_mult = 1.2

                    # Assign RoomType Images
                    room_type_images = {
                        "Standard Room": "https://images.unsplash.com/photo-1560440021-33f9bde03080?auto=format&fit=crop&w=800&q=80",
                        "Deluxe Room": "https://images.unsplash.com/photo-1590447179489-d779722d390b?auto=format&fit=crop&w=800&q=80",
                        "Family Suite": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80",
                        "Executive Suite": "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=800&q=80",
                        "Penthouse": "https://images.unsplash.com/photo-1578683010236-d716f9d3f2f7?auto=format&fit=crop&w=800&q=80",
                    }
                    
                    for rt_temp in brand_rts:
                         # Vary price slightly per hotel
                        price = int(rt_temp["price_base"] * price_mult * (0.9 + random.random()*0.2))
                        
                        rt = RoomType(
                            hotel=hotel,
                            name=rt_temp["name"],
                            description=f"A comfortable stay in {city_name}.",
                            price_per_night=price,
                            capacity=rt_temp["cap"],
                            inventory=random.randint(5, 20),
                            image_url=room_type_images.get(rt_temp["name"], "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80")
                        )
                        
                        # Assign Amenities
                        possible_amenities = list(amenities.values())
                        if brand_name == "Grand Apex":
                             rt.amenities = possible_amenities
                        elif brand_name == "Metro Express":
                             rt.amenities = random.sample(possible_amenities, k=3)
                        else:
                             rt.amenities = random.sample(possible_amenities, k=8)
                        
                        db.session.add(rt)
        
        db.session.commit()
        print(f"Created {len(created_hotels)} hotels across {len(cities)} cities.")

        print("Seeding Users & Reviews...")
        u1 = User(username='traveler_john', email='john@example.com', password_hash=generate_password_hash('password'), membership_level='Silver', points=5000)
        u2 = User(username='vip_sarah', email='sarah@example.com', password_hash=generate_password_hash('password'), membership_level='Platinum', points=125000)
        db.session.add_all([u1, u2])
        db.session.commit()
        
        # Add some reviews
        for h in created_hotels:
            if random.random() > 0.5: # 50% chance a hotel has a review
                rev = Review(
                    user_id=random.choice([u1.id, u2.id]), 
                    hotel_id=h.id, 
                    rating=random.randint(3, 5), 
                    comment="Great stay!"
                )
                db.session.add(rev)
        
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    seed()
