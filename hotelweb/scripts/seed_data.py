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
            "Conference Room", "Kids Club", "Ocean View", "Smart TV", "Mini Bar", "Rooftop Terrace", "Yoga Studio", "Breakfast"
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
            {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
            {"name": "Amsterdam", "lat": 52.3676, "lon": 4.9041},
            {"name": "Vienna", "lat": 48.2082, "lon": 16.3738},
            {"name": "Madrid", "lat": 40.4168, "lon": -3.7038},
            {"name": "Miami", "lat": 25.7617, "lon": -80.1918},
            {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
            {"name": "Toronto", "lat": 43.6532, "lon": -79.3832},
            {"name": "Seoul", "lat": 37.5665, "lon": 126.9780},
            {"name": "Bangkok", "lat": 13.7563, "lon": 100.5018}
        ]

        # Pool of images - using ONLY local images (all external images have been downloaded)
        # Local images available: hotel_0.jpg to hotel_29.jpg (30 images total)
        local_hotel_images = [
            "/static/img/hotels/hotel_0.jpg",
            "/static/img/hotels/hotel_1.jpg",
            "/static/img/hotels/hotel_2.jpg",
            "/static/img/hotels/hotel_3.jpg",
            "/static/img/hotels/hotel_4.jpg",
            "/static/img/hotels/hotel_5.jpg",
            "/static/img/hotels/hotel_6.jpg",
            "/static/img/hotels/hotel_7.jpg",
            "/static/img/hotels/hotel_8.jpg",
            "/static/img/hotels/hotel_9.jpg",
            "/static/img/hotels/hotel_11.jpg",
            "/static/img/hotels/hotel_12.jpg",
            "/static/img/hotels/hotel_13.jpg",
            "/static/img/hotels/hotel_15.jpg",
            "/static/img/hotels/hotel_16.jpg",
            "/static/img/hotels/hotel_17.jpg",
            "/static/img/hotels/hotel_18.jpg",
            "/static/img/hotels/hotel_19.jpg",
            "/static/img/hotels/hotel_20.jpg",
            "/static/img/hotels/hotel_21.jpg",
            "/static/img/hotels/hotel_22.jpg",
            "/static/img/hotels/hotel_23.jpg",
            "/static/img/hotels/hotel_24.jpg",
            "/static/img/hotels/hotel_25.jpg",
            "/static/img/hotels/hotel_26.jpg",
            "/static/img/hotels/hotel_27.jpg",
            "/static/img/hotels/hotel_28.jpg",
            "/static/img/hotels/hotel_29.jpg"
        ]
        
        # All brands use the same local image pool (no external URLs)
        images_pool = {
            "Grand Apex": local_hotel_images,
            "Urban Pulse": local_hotel_images,
            "Family Haven": local_hotel_images,
            "Metro Express": local_hotel_images
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

            # For each city, generate more hotels per brand for richer data
            for brand_name, brand_obj in brands.items():
                # More hotels: Grand Apex (2-3), Urban Pulse/Family Haven (2-4), Metro Express (2-3)
                if brand_name == "Grand Apex":
                    num_hotels = random.choice([2, 2, 3])
                elif brand_name == "Metro Express":
                    num_hotels = random.choice([2, 2, 3])
                else:  # Urban Pulse, Family Haven
                    num_hotels = random.choice([2, 3, 3, 4])
                
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

                    # Set breakfast price based on star rating: 5-star=$50, 4-star=$40, 3-star=$30, 2-star=$20, 1-star=$10
                    breakfast_price_map = {5: 50.00, 4: 40.00, 3: 30.00, 2: 20.00, 1: 10.00}
                    breakfast_price = breakfast_price_map.get(stars, 25.00)

                    hotel = Hotel(
                        name=hotel_name,
                        city=city_name,
                        address=f"{random.randint(1, 999)} {city_name} Ave",
                        description=f"Experience the unique charm of {city_name} with {brand_name}'s signature hospitality.",
                        stars=stars,
                        image_url=random.choice(images_pool[brand_name]),
                        latitude=base_lat + lat_offset,
                        longitude=base_lon + lon_offset,
                        brand=brand_obj,
                        breakfast_price=breakfast_price
                    )
                    db.session.add(hotel)
                    created_hotels.append(hotel)

                    # Create Room Types - More variety for luxury hotels, fewer for budget hotels
                    # Define comprehensive room type templates
                    rt_templates = [
                        {"name": "Standard Room", "price_base": 100, "cap": 2, "inventory_range": (10, 25)},
                        {"name": "Superior Room", "price_base": 130, "cap": 2, "inventory_range": (8, 20)},
                        {"name": "Deluxe Room", "price_base": 150, "cap": 2, "inventory_range": (8, 18)},
                        {"name": "Junior Suite", "price_base": 220, "cap": 2, "inventory_range": (5, 12)},
                        {"name": "Family Suite", "price_base": 250, "cap": 4, "inventory_range": (5, 15)},
                        {"name": "Executive Suite", "price_base": 400, "cap": 2, "inventory_range": (2, 8)},
                        {"name": "Presidential Suite", "price_base": 800, "cap": 4, "inventory_range": (1, 4)},
                        {"name": "Penthouse", "price_base": 1000, "cap": 4, "inventory_range": (1, 3)}
                    ]
                    
                    # Filter templates by brand tier - Luxury hotels get more room types
                    if brand_name == "Grand Apex":
                        # Luxury: 6-8 room types (no Standard, include all premium options)
                        available_rts = rt_templates[1:]  # Skip Standard Room
                        num_room_types = random.choice([6, 7, 8])
                        brand_rts = random.sample(available_rts, min(num_room_types, len(available_rts)))
                        # Ensure Penthouse is always included for luxury hotels
                        if not any(rt["name"] == "Penthouse" for rt in brand_rts):
                            penthouse_rt = next(rt for rt in rt_templates if rt["name"] == "Penthouse")
                            if penthouse_rt not in brand_rts:
                                brand_rts.append(penthouse_rt)
                        price_mult = 2.0
                    elif brand_name == "Metro Express":
                        # Budget: 2-3 room types (only basic options)
                        brand_rts = rt_templates[:3]  # Standard, Superior, Deluxe
                        num_room_types = random.choice([2, 2, 3])
                        brand_rts = brand_rts[:num_room_types]
                        price_mult = 0.8
                    else:
                        # Mid-tier: 4-5 room types (Urban Pulse, Family Haven)
                        available_rts = rt_templates[:6]  # Up to Executive Suite
                        num_room_types = random.choice([4, 4, 5])
                        brand_rts = random.sample(available_rts, min(num_room_types, len(available_rts)))
                        price_mult = 1.2

                    # Assign RoomType Images - using ONLY local images
                    room_type_images = {
                        "Standard Room": random.choice(local_hotel_images),
                        "Superior Room": random.choice(local_hotel_images),
                        "Deluxe Room": random.choice(local_hotel_images),
                        "Junior Suite": random.choice(local_hotel_images),
                        "Family Suite": random.choice(local_hotel_images),
                        "Executive Suite": random.choice(local_hotel_images),
                        "Presidential Suite": random.choice(local_hotel_images),
                        "Penthouse": random.choice(local_hotel_images),
                    }

                    for rt_temp in brand_rts:
                         # Vary price slightly per hotel
                        price = int(rt_temp["price_base"] * price_mult * (0.9 + random.random()*0.2))
                        
                        # Inventory: Higher tier rooms have fewer units (luxury scarcity)
                        inventory_min, inventory_max = rt_temp["inventory_range"]
                        inventory = random.randint(inventory_min, inventory_max)
                        
                        rt = RoomType(
                            hotel=hotel,
                            name=rt_temp["name"],
                            description=f"A comfortable stay in {city_name}.",
                            price_per_night=price,
                            capacity=rt_temp["cap"],
                            inventory=inventory,
                            image_url=room_type_images.get(rt_temp["name"], random.choice(local_hotel_images))
                        )
                        
                        # Assign Amenities
                        possible_amenities = list(amenities.values())
                        if brand_name == "Grand Apex":
                             rt.amenities = possible_amenities
                        elif brand_name == "Metro Express":
                             rt.amenities = random.sample(possible_amenities, k=3)
                        else:
                             rt.amenities = random.sample(possible_amenities, k=8)
                        
                        # Ensure all room types have Breakfast amenity
                        if "Breakfast" in amenities and amenities["Breakfast"] not in rt.amenities:
                            rt.amenities.append(amenities["Breakfast"])
                        
                        db.session.add(rt)
        
        db.session.commit()
        
        # Count room types by brand
        total_room_types = 0
        room_types_by_brand = {}
        for hotel in created_hotels:
            brand_name = hotel.brand.name
            room_count = len(hotel.room_types)
            total_room_types += room_count
            if brand_name not in room_types_by_brand:
                room_types_by_brand[brand_name] = []
            room_types_by_brand[brand_name].append(room_count)
        
        print(f"Created {len(created_hotels)} hotels across {len(cities)} cities.")
        print(f"Total room types created: {total_room_types}")
        print("Room types per brand (average):")
        for brand_name, counts in room_types_by_brand.items():
            avg_rooms = sum(counts) / len(counts) if counts else 0
            print(f"  {brand_name}: {avg_rooms:.1f} room types per hotel (range: {min(counts)}-{max(counts)})")

        print("Seeding Test Users (covering all 5 membership tiers)...")
        
        # Create test users for each membership tier
        test_users = [
            # Club Member (0-49,999 lifetime points)
            {
                'username': 'club_member_01',
                'email': 'club01@test.com',
                'password': 'password',
                'membership_level': 'Club Member',
                'lifetime_points': 25000,
                'points': 5000,
                'nights_stayed': 5
            },
            {
                'username': 'club_member_02',
                'email': 'club02@test.com',
                'password': 'password',
                'membership_level': 'Club Member',
                'lifetime_points': 40000,
                'points': 8000,
                'nights_stayed': 8
            },
            
            # Silver Elite (50,000-99,999 lifetime points)
            {
                'username': 'silver_elite_01',
                'email': 'silver01@test.com',
                'password': 'password',
                'membership_level': 'Silver Elite',
                'lifetime_points': 60000,
                'points': 12000,
                'nights_stayed': 12
            },
            {
                'username': 'silver_elite_02',
                'email': 'silver02@test.com',
                'password': 'password',
                'membership_level': 'Silver Elite',
                'lifetime_points': 85000,
                'points': 15000,
                'nights_stayed': 15
            },
            
            # Gold Elite (100,000-499,999 lifetime points)
            {
                'username': 'gold_elite_01',
                'email': 'gold01@test.com',
                'password': 'password',
                'membership_level': 'Gold Elite',
                'lifetime_points': 150000,
                'points': 30000,
                'nights_stayed': 25
            },
            {
                'username': 'gold_elite_02',
                'email': 'gold02@test.com',
                'password': 'password',
                'membership_level': 'Gold Elite',
                'lifetime_points': 350000,
                'points': 60000,
                'nights_stayed': 35
            },
            
            # Diamond Elite (500,000-999,999 lifetime points)
            {
                'username': 'diamond_elite_01',
                'email': 'diamond01@test.com',
                'password': 'password',
                'membership_level': 'Diamond Elite',
                'lifetime_points': 650000,
                'points': 100000,
                'nights_stayed': 75
            },
            {
                'username': 'diamond_elite_02',
                'email': 'diamond02@test.com',
                'password': 'password',
                'membership_level': 'Diamond Elite',
                'lifetime_points': 850000,
                'points': 150000,
                'nights_stayed': 85
            },
            
            # Platinum Elite (1,000,000+ lifetime points)
            {
                'username': 'platinum_elite_01',
                'email': 'platinum01@test.com',
                'password': 'password',
                'membership_level': 'Platinum Elite',
                'lifetime_points': 1200000,
                'points': 200000,
                'nights_stayed': 220
            },
            {
                'username': 'platinum_elite_02',
                'email': 'platinum02@test.com',
                'password': 'password',
                'membership_level': 'Platinum Elite',
                'lifetime_points': 2500000,
                'points': 400000,
                'nights_stayed': 300
            },
        ]
        
        created_users = []
        for user_data in test_users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                membership_level=user_data['membership_level'],
                lifetime_points=user_data['lifetime_points'],
                points=user_data['points'],
                nights_stayed=user_data['nights_stayed']
            )
            db.session.add(user)
            created_users.append(user)
        
        db.session.commit()
        print(f"  Created {len(created_users)} test users covering all 5 membership tiers")
        print("  Club Member: club01@test.com, club02@test.com (password: password)")
        print("  Silver Elite: silver01@test.com, silver02@test.com (password: password)")
        print("  Gold Elite: gold01@test.com, gold02@test.com (password: password)")
        print("  Diamond Elite: diamond01@test.com, diamond02@test.com (password: password)")
        print("  Platinum Elite: platinum01@test.com, platinum02@test.com (password: password)")
        
        # Add some reviews from different tier users (without booking_id for seed data)
        print("Adding sample reviews...")
        review_count = 0
        for h in created_hotels:
            if random.random() > 0.4: # 60% chance a hotel has a review
                reviewer = random.choice(created_users)
                rev = Review(
                    user_id=reviewer.id, 
                    hotel_id=h.id, 
                    rating=random.randint(3, 5), 
                    comment=random.choice([
                        "Great stay! Highly recommend.",
                        "Excellent service and comfortable rooms.",
                        "Beautiful hotel with amazing amenities.",
                        "Perfect location and friendly staff.",
                        "Wonderful experience, will come back!",
                        "Nice hotel, good value for money.",
                        "Impressive facilities and great breakfast."
                    ])
                )
                db.session.add(rev)
                review_count += 1
        
        db.session.commit()
        print(f"  Added {review_count} reviews from various tier members")
        
        # Create Admin Account (if doesn't exist)
        print("Creating Admin Account...")
        admin = User.query.filter_by(email='admin@lumina.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@lumina.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("  Admin created: admin@lumina.com / admin123")
        else:
            print("  Admin already exists")
        
        # Create Staff Account (if doesn't exist)
        print("Creating Staff Account...")
        staff = User.query.filter_by(email='staff@lumina.com').first()
        if not staff:
            staff = User(
                username='staff',
                email='staff@lumina.com',
                password_hash=generate_password_hash('staff123'),
                role='staff'
            )
            db.session.add(staff)
            db.session.flush()  # Flush to get staff.id before assigning hotels
            # Assign first 3 hotels to staff for testing
            if len(created_hotels) >= 3:
                staff.assigned_hotels = created_hotels[:3]
            db.session.commit()
            print("  Staff created: staff@lumina.com / staff123")
            # For lazy='dynamic' relationships, use .count() instead of len()
            print(f"  Assigned {staff.assigned_hotels.count()} hotels to staff")
        else:
            print("  Staff already exists")
        
        print("Done!")

if __name__ == '__main__':
    seed()
