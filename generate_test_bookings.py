"""
Generate diverse test bookings for testing My Stays functionality
"""
import os
import sys
from datetime import date, timedelta, datetime
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User, Hotel, RoomType, Booking, PointsTransaction

def generate_test_bookings():
    app = create_app()
    
    with app.app_context():
        # Find or create test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='testuser@gmail.com',
                points=0,
                lifetime_points=0,
                nights_stayed=0,
                membership_level='Member'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print(f"Created test user: testuser")
        else:
            print(f"Using existing user: {test_user.username}")
        
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
        
        # Clear existing bookings for test user
        Booking.query.filter_by(user_id=test_user.id).delete()
        PointsTransaction.query.filter_by(user_id=test_user.id).delete()
        test_user.points = 0
        test_user.lifetime_points = 0
        test_user.nights_stayed = 0
        test_user.membership_level = 'Member'
        db.session.commit()
        
        bookings_created = []
        today = date.today()
        
        # 1. Past bookings (6-8 bookings, 1-12 months ago)
        print("\nCreating past bookings...")
        for i in range(random.randint(6, 8)):
            hotel = random.choice(hotels_with_rooms)
            room_type = random.choice(hotel.room_types)
            
            # Random date 1-12 months ago
            months_ago = random.randint(1, 12)
            check_out = today - timedelta(days=random.randint(months_ago * 30, months_ago * 30 + 20))
            nights = random.randint(2, 5)
            check_in = check_out - timedelta(days=nights)
            
            booking = create_booking(test_user, room_type, check_in, check_out, nights)
            bookings_created.append(('past', booking))
            print(f"  ✓ Past stay at {hotel.name}: {check_in} to {check_out}")
        
        # 2. Upcoming bookings (3-5 bookings, 1-60 days ahead)
        print("\nCreating upcoming bookings...")
        for i in range(random.randint(3, 5)):
            hotel = random.choice(hotels_with_rooms)
            room_type = random.choice(hotel.room_types)
            
            # Random date 1-60 days ahead
            check_in = today + timedelta(days=random.randint(1, 60))
            nights = random.randint(2, 4)
            check_out = check_in + timedelta(days=nights)
            
            booking = create_booking(test_user, room_type, check_in, check_out, nights)
            bookings_created.append(('upcoming', booking))
            print(f"  ✓ Upcoming stay at {hotel.name}: {check_in} to {check_out}")
        
        # 3. Current booking (1 booking, checked in yesterday)
        print("\nCreating current booking...")
        hotel = random.choice(hotels_with_rooms)
        room_type = random.choice(hotel.room_types)
        check_in = today - timedelta(days=1)
        check_out = today + timedelta(days=2)
        nights = (check_out - check_in).days
        
        booking = create_booking(test_user, room_type, check_in, check_out, nights)
        bookings_created.append(('current', booking))
        print(f"  ✓ Current stay at {hotel.name}: {check_in} to {check_out}")
        
        # 4. Cancelled bookings (2-3 bookings)
        print("\nCreating cancelled bookings...")
        for i in range(random.randint(2, 3)):
            hotel = random.choice(hotels_with_rooms)
            room_type = random.choice(hotel.room_types)
            
            # Mix of past and future cancelled bookings
            if random.choice([True, False]):
                # Past cancelled
                check_out = today - timedelta(days=random.randint(10, 90))
            else:
                # Future cancelled
                check_out = today + timedelta(days=random.randint(10, 60))
            
            nights = random.randint(2, 4)
            check_in = check_out - timedelta(days=nights)
            
            booking = create_booking(test_user, room_type, check_in, check_out, nights, cancelled=True)
            bookings_created.append(('cancelled', booking))
            print(f"  ✓ Cancelled booking at {hotel.name}: {check_in} to {check_out}")
        
        db.session.commit()
        
        # Update user tier based on lifetime points
        test_user.calculate_tier()
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"Test data generation complete!")
        print(f"{'='*60}")
        print(f"User: {test_user.username}")
        print(f"Membership Tier: {test_user.membership_level}")
        print(f"Current Points: {test_user.points:,}")
        print(f"Lifetime Points: {test_user.lifetime_points:,}")
        print(f"Nights Stayed: {test_user.nights_stayed}")
        print(f"\nBookings created:")
        print(f"  Past: {len([b for t, b in bookings_created if t == 'past'])}")
        print(f"  Upcoming: {len([b for t, b in bookings_created if t == 'upcoming'])}")
        print(f"  Current: {len([b for t, b in bookings_created if t == 'current'])}")
        print(f"  Cancelled: {len([b for t, b in bookings_created if t == 'cancelled'])}")
        print(f"  Total: {len(bookings_created)}")
        print(f"\nYou can now log in with:")
        print(f"  Email: testuser@gmail.com")
        print(f"  Password: password123")

def create_booking(user, room_type, check_in, check_out, nights, cancelled=False):
    """Create a booking with proper billing and points calculation"""
    rooms_count = random.randint(1, 2)
    
    # Calculate billing
    base_rate = float(room_type.price_per_night)
    subtotal = base_rate * nights * rooms_count
    taxes = subtotal * 0.10
    fees = subtotal * 0.05
    total_cost = subtotal + taxes + fees
    
    # Calculate points (only for non-cancelled bookings)
    if not cancelled:
        base_points = int(total_cost * 10)
        multiplier = user.get_points_multiplier()
        points_earned = int(base_points * multiplier)
    else:
        points_earned = 0
    
    # Create booking
    booking = Booking(
        user_id=user.id,
        roomtype_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        rooms_count=rooms_count,
        status='CANCELLED' if cancelled else 'CONFIRMED',
        base_rate=base_rate,
        subtotal=subtotal,
        taxes=taxes,
        fees=fees,
        total_cost=total_cost,
        points_earned=points_earned,
        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
    )
    
    db.session.add(booking)
    db.session.flush()
    
    # Update user stats (only for confirmed bookings)
    if not cancelled:
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
    generate_test_bookings()
