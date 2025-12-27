#!/usr/bin/env python3
"""Update all user tiers to match new tier system"""

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User

app = create_app()

with app.app_context():
    # Get all users
    users = User.query.all()
    
    print(f"Updating tiers for {len(users)} users...")
    
    for user in users:
        old_tier = user.membership_level
        user.calculate_tier()
        new_tier = user.membership_level
        
        if old_tier != new_tier:
            print(f"  {user.username}: {old_tier} -> {new_tier} ({user.lifetime_points:,} points)")
        else:
            print(f"  {user.username}: {new_tier} (unchanged, {user.lifetime_points:,} points)")
    
    db.session.commit()
    print("\nTiers updated successfully!")
