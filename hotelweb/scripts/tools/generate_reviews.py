"""
Generate review data for all hotels
Each hotel will have multiple reviews from different users
"""

import os
import sys
from datetime import datetime, timedelta, timezone
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User, Hotel, Review

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

def generate_reviews():
    app = create_app()
    
    with app.app_context():
        print("Generating reviews for all hotels...")
        
        # Get all hotels
        hotels = Hotel.query.all()
        if not hotels:
            print("No hotels found in database!")
            return
        
        print(f"Found {len(hotels)} hotels")
        
        # Get all users (or create some test users if needed)
        users = User.query.all()
        if len(users) < 5:
            print("Creating additional test users for reviews...")
            test_usernames = ['reviewer_alice', 'reviewer_bob', 'reviewer_charlie', 'reviewer_diana', 'reviewer_edward']
            for username in test_usernames:
                if not User.query.filter_by(username=username).first():
                    user = User(
                        username=username,
                        email=f'{username}@example.com',
                        points=random.randint(1000, 50000),
                        lifetime_points=random.randint(5000, 100000),
                        nights_stayed=random.randint(5, 50),
                        membership_level=random.choice(['Club Member', 'Silver Elite', 'Gold Elite', 'Diamond Elite', 'Platinum Elite'])
                    )
                    user.set_password('password123')
                    db.session.add(user)
            db.session.commit()
            users = User.query.all()
        
        print(f"Using {len(users)} users for reviews")
        
        # Clear existing reviews (optional - comment out if you want to keep existing reviews)
        # Review.query.delete()
        # db.session.commit()
        # print("Cleared existing reviews")
        
        reviews_created = 0
        today = datetime.now(timezone.utc)
        
        # Generate reviews for each hotel
        for hotel in hotels:
            # Each hotel gets 3-8 reviews
            num_reviews = random.randint(3, 8)
            
            for i in range(num_reviews):
                # Random user
                user = random.choice(users)
                
                # Random rating (weighted towards positive reviews)
                # 60% chance of 4-5 stars, 30% chance of 3 stars, 10% chance of 1-2 stars
                rand = random.random()
                if rand < 0.6:
                    rating = random.choice([4, 5])
                elif rand < 0.9:
                    rating = 3
                else:
                    rating = random.choice([1, 2])
                
                # Random comment
                comment = random.choice(REVIEW_COMMENTS)
                
                # Random date within last 6 months
                days_ago = random.randint(1, 180)
                created_at = today - timedelta(days=days_ago)
                
                # Check if this user already reviewed this hotel
                existing = Review.query.filter_by(user_id=user.id, hotel_id=hotel.id).first()
                if existing:
                    continue  # Skip if user already reviewed this hotel
                
                review = Review(
                    user_id=user.id,
                    hotel_id=hotel.id,
                    rating=rating,
                    comment=comment,
                    created_at=created_at
                )
                db.session.add(review)
                reviews_created += 1
        
        db.session.commit()
        
        print(f"\n✓ Created {reviews_created} reviews across {len(hotels)} hotels")
        
        # Show summary
        print("\nReview summary by hotel:")
        for hotel in hotels:
            review_count = Review.query.filter_by(hotel_id=hotel.id).count()
            if review_count > 0:
                avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(hotel_id=hotel.id).scalar()
                print(f"  {hotel.name}: {review_count} reviews, avg rating: {avg_rating:.1f}")
        
        print("\nDone!")

if __name__ == '__main__':
    generate_reviews()

