"""
Create test accounts with specific number of stays and reviews
- Account 1: 15 stays with reviews
- Account 2: 46 stays with reviews  
- Account 3: 211 stays with reviews
"""

import os
import sys
from datetime import date, timedelta, datetime
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User, Hotel, RoomType, Booking, Review, PointsTransaction

# Sample review comments
REVIEW_COMMENTS = [
    "Excellent stay! The room was clean and comfortable, and the staff was very friendly.",
    "Great hotel with amazing amenities. Would definitely stay here again!",
    "Perfect location and wonderful service. Highly recommend!",
    "Beautiful hotel with stunning views. The breakfast was delicious.",
    "Very comfortable rooms and excellent customer service. Will come back!",
    "Loved the modern design and convenient location. Great value for money.",
    "Outstanding experience! The staff went above and beyond to make our stay memorable.",
    "Clean, comfortable, and well-maintained. The pool area was fantastic.",
    "Great stay overall. The room was spacious and the bed was very comfortable.",
    "Wonderful hotel with excellent facilities. The restaurant had great food.",
    "Perfect for families! The kids loved the pool and the staff was very accommodating.",
    "Beautiful property with great amenities. The spa was a nice touch.",
    "Comfortable stay with good service. The location was convenient for sightseeing.",
    "Nice hotel with friendly staff. The room had everything we needed.",
    "Excellent value! Clean rooms, good service, and great location.",
    "Loved our stay! The hotel exceeded our expectations in every way.",
    "Great experience overall. The concierge was very helpful with recommendations.",
    "Comfortable and clean. The breakfast buffet had a good variety.",
    "Nice hotel with modern amenities. Would stay here again.",
    "Excellent service and comfortable rooms. The location was perfect for our needs.",
    "Good stay, but the Wi-Fi could be faster. Otherwise everything was great.",
    "Nice hotel, though the rooms could use some updating. Service was good.",
    "Decent stay. The location was convenient but the rooms were a bit small.",
    "Average experience. The hotel was clean but nothing exceptional.",
    "The hotel was okay, but the service could be improved. Room was clean though."
]

def create_test_accounts():
    app = create_app()
    
    with app.app_context():
        # Get all hotels with room types
        hotels = Hotel.query.all()
        if not hotels:
            print("No hotels found in database!")
            return
        
        hotels_with_rooms = [h for h in hotels if h.room_types]
        if not hotels_with_rooms:
            print("No hotels with room types found!")
            return
        
        print(f"Found {len(hotels_with_rooms)} hotels with rooms")
        
        # Test account configurations
        test_accounts = [
            {'username': 'testuser_15', 'email': 'testuser15@example.com', 'stays': 15, 'reviews_per_stay': 0.8},  # 80% of stays have reviews
            {'username': 'testuser_46', 'email': 'testuser46@example.com', 'stays': 46, 'reviews_per_stay': 0.7},  # 70% of stays have reviews
            {'username': 'testuser_211', 'email': 'testuser211@example.com', 'stays': 211, 'reviews_per_stay': 0.6}  # 60% of stays have reviews
        ]
        
        today = date.today()
        
        for account_config in test_accounts:
            username = account_config['username']
            email = account_config['email']
            num_stays = account_config['stays']
            review_rate = account_config['reviews_per_stay']
            
            print(f"\n{'='*60}")
            print(f"Creating account: {username} with {num_stays} stays")
            print(f"{'='*60}")
            
            # Find or create user
            user = User.query.filter_by(username=username).first()
            if user:
                # Clear existing data
                print(f"  Clearing existing data for {username}...")
                Booking.query.filter_by(user_id=user.id).delete()
                Review.query.filter_by(user_id=user.id).delete()
                PointsTransaction.query.filter_by(user_id=user.id).delete()
                user.points = 0
                user.lifetime_points = 0
                user.nights_stayed = 0
                user.membership_level = 'Club Member'
                db.session.commit()
            else:
                # Create new user
                user = User(
                    username=username,
                    email=email,
                    points=0,
                    lifetime_points=0,
                    nights_stayed=0,
                    membership_level='Club Member'
                )
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()
                print(f"  Created new user: {username}")
            
            # Generate bookings
            total_nights = 0
            bookings_created = []
            
            # Distribute stays over time (more recent stays are more frequent)
            # For 15 stays: spread over ~12 months
            # For 46 stays: spread over ~24 months
            # For 211 stays: spread over ~36 months
            if num_stays <= 15:
                months_span = 12
            elif num_stays <= 46:
                months_span = 24
            else:
                months_span = 36
            
            print(f"  Generating {num_stays} completed stays...")
            
            for i in range(num_stays):
                # Choose random hotel and room type
                hotel = random.choice(hotels_with_rooms)
                room_type = random.choice(hotel.room_types)
                
                # Generate check-out date (completed stays, so check_out <= today)
                # More recent dates are more likely
                days_ago = random.randint(1, months_span * 30)
                # Weight towards recent dates
                if random.random() < 0.3:  # 30% chance of very recent (last 30 days)
                    days_ago = random.randint(1, 30)
                elif random.random() < 0.6:  # 30% chance of recent (last 90 days)
                    days_ago = random.randint(30, 90)
                
                check_out = today - timedelta(days=days_ago)
                
                # Random nights (1-5 nights per stay)
                nights = random.randint(1, 5)
                check_in = check_out - timedelta(days=nights)
                
                # Create booking
                booking = create_booking(user, room_type, check_in, check_out, nights)
                bookings_created.append(booking)
                total_nights += nights
                
                if (i + 1) % 10 == 0:
                    print(f"    Created {i + 1}/{num_stays} bookings...")
            
            db.session.commit()
            print(f"  ✓ Created {len(bookings_created)} bookings, {total_nights} total nights")
            
            # Generate reviews for completed stays
            num_reviews = int(num_stays * review_rate)
            bookings_to_review = random.sample(bookings_created, min(num_reviews, len(bookings_created)))
            
            print(f"  Generating {len(bookings_to_review)} reviews...")
            
            for booking in bookings_to_review:
                # Random rating (weighted towards positive)
                rand = random.random()
                if rand < 0.6:
                    rating = random.choice([4, 5])
                elif rand < 0.9:
                    rating = 3
                else:
                    rating = random.choice([1, 2])
                
                # Random comment
                comment = random.choice(REVIEW_COMMENTS)
                
                # Review date should be after check_out
                review_date = booking.check_out + timedelta(days=random.randint(1, 30))
                
                review = Review(
                    user_id=user.id,
                    hotel_id=booking.room_type.hotel.id,
                    booking_id=booking.id,
                    rating=rating,
                    comment=comment,
                    created_at=datetime.combine(review_date, datetime.min.time())
                )
                db.session.add(review)
            
            db.session.commit()
            print(f"  ✓ Created {len(bookings_to_review)} reviews")
            
            # Update user tier based on lifetime points and nights
            user.calculate_tier()
            db.session.commit()
            
            # Print summary
            print(f"\n  Account Summary:")
            print(f"    Username: {username}")
            print(f"    Email: {email}")
            print(f"    Password: password123")
            print(f"    Total Stays: {len(bookings_created)}")
            print(f"    Total Nights: {user.nights_stayed}")
            print(f"    Total Reviews: {len(bookings_to_review)}")
            print(f"    Current Points: {user.points:,}")
            print(f"    Lifetime Points: {user.lifetime_points:,}")
            print(f"    Membership Tier: {user.membership_level}")
        
        print(f"\n{'='*60}")
        print(f"All test accounts created successfully!")
        print(f"{'='*60}")
        print(f"\nLogin credentials:")
        for account_config in test_accounts:
            print(f"  {account_config['username']}:")
            print(f"    Email: {account_config['email']}")
            print(f"    Password: password123")
            print(f"    Stays: {account_config['stays']}")
        print(f"\nDone!")

def create_booking(user, room_type, check_in, check_out, nights):
    """Create a completed booking with proper billing and points calculation"""
    rooms_count = random.randint(1, 2)
    
    # Calculate billing
    base_rate = float(room_type.price_per_night)
    subtotal = base_rate * nights * rooms_count
    taxes = subtotal * 0.10
    fees = subtotal * 0.05
    total_cost = subtotal + taxes + fees
    
    # Calculate points
    # Formula: 1 dollar = 10 base points, then multiply by tier multiplier
    per_night_total = base_rate * 1.15  # Room rate with taxes/fees equivalent
    base_points_per_night = int(per_night_total * 10)  # 10 points per $1
    multiplier = user.get_points_multiplier()
    points_per_night = int(base_points_per_night * multiplier)
    points_earned = points_per_night * nights * rooms_count
    
    # Create booking (all are completed stays)
    booking = Booking(
        user_id=user.id,
        roomtype_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        rooms_count=rooms_count,
        status='CONFIRMED',
        base_rate=base_rate,
        subtotal=subtotal,
        taxes=taxes,
        fees=fees,
        total_cost=total_cost,
        points_earned=points_earned,
        created_at=datetime.combine(check_in, datetime.min.time()) - timedelta(days=random.randint(1, 7))
    )
    
    db.session.add(booking)
    db.session.flush()
    
    # Update user stats
    user.points += points_earned
    user.lifetime_points += points_earned
    user.nights_stayed += nights
    
    # Create points transaction
    transaction = PointsTransaction(
        user_id=user.id,
        booking_id=booking.id,
        points=points_earned,
        transaction_type='EARNED',
        description=f'Stay at {room_type.hotel.name} - {nights} night(s)',
        created_at=booking.created_at
    )
    db.session.add(transaction)
    
    return booking

if __name__ == '__main__':
    create_test_accounts()

