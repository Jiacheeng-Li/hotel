import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from hotelweb.app import create_app
from hotelweb.extensions import db

app = create_app()

def migrate():
    with app.app_context():
        print("Starting PaymentMethod migration...")
        
        # Create PaymentMethod table
        # Using db.create_all() is safe as it only creates tables that don't exist
        print("Creating PaymentMethod table...")
        db.create_all()
        
        print("Migration completed.")

if __name__ == '__main__':
    migrate()

