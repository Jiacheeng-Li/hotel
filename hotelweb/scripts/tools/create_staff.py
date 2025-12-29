"""
Create a test staff account with assigned hotels
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User, Hotel

def create_staff():
    app = create_app()
    with app.app_context():
        # Check if staff already exists
        staff = User.query.filter_by(email='staff@lumina.com').first()
        if staff:
            print(f"Staff account already exists!")
            print(f"  Email: {staff.email}")
            print(f"  Username: {staff.username}")
            print(f"  Role: {staff.role}")
            assigned = staff.assigned_hotels.all()
            print(f"  Assigned Hotels: {len(assigned)}")
            for hotel in assigned:
                print(f"    - {hotel.name}")
            return
        
        # Get first 3 hotels to assign
        hotels = Hotel.query.limit(3).all()
        if not hotels:
            print("No hotels found in database. Please seed the database first.")
            return
        
        # Create staff user
        staff = User(
            username='staff',
            email='staff@lumina.com',
            role='staff'
        )
        staff.set_password('staff123')
        
        # Assign hotels
        staff.assigned_hotels = hotels
        
        db.session.add(staff)
        db.session.commit()
        
        print("=" * 60)
        print("Staff account created successfully!")
        print("=" * 60)
        print(f"Email: {staff.email}")
        print(f"Username: {staff.username}")
        print(f"Password: staff123")
        print(f"Role: {staff.role}")
        print(f"\nAssigned Hotels ({len(hotels)}):")
        for hotel in hotels:
            print(f"  - {hotel.name} ({hotel.city})")
        print("=" * 60)
        print("\nYou can now login at: /staff/login")

if __name__ == '__main__':
    create_staff()

