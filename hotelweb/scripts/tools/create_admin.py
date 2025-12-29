"""
Create admin account
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@lumina.com').first()
        if admin:
            print(f"Admin account already exists!")
            print(f"  Email: {admin.email}")
            print(f"  Username: {admin.username}")
            print(f"  Role: {admin.role}")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@lumina.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 60)
        print("Admin account created successfully!")
        print("=" * 60)
        print(f"Email: {admin.email}")
        print(f"Username: {admin.username}")
        print(f"Password: admin123")
        print(f"Role: {admin.role}")
        print("=" * 60)
        print("\nYou can now login at: /admin/login")

if __name__ == '__main__':
    create_admin()

