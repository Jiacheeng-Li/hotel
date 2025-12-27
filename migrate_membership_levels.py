#!/usr/bin/env python3
"""
Migration script to normalize all membership_level values to new naming convention:
- Old: 'Gold', 'Silver', 'Diamond', 'Platinum', 'Member', 'Ambassador'
- New: 'Club Member', 'Silver Elite', 'Gold Elite', 'Diamond Elite', 'Platinum Elite'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hotelweb.app import create_app
from hotelweb.extensions import db
from hotelweb.models import User

def normalize_membership_level(old_level):
    """Convert old membership level names to new standard names"""
    mapping = {
        'Member': 'Club Member',
        'Club Member': 'Club Member',  # Already correct
        'Silver': 'Silver Elite',
        'Silver Elite': 'Silver Elite',  # Already correct
        'Gold': 'Gold Elite',
        'Gold Elite': 'Gold Elite',  # Already correct
        'Diamond': 'Diamond Elite',
        'Diamond Elite': 'Diamond Elite',  # Already correct
        'Platinum': 'Platinum Elite',
        'Platinum Elite': 'Platinum Elite',  # Already correct
        'Ambassador': 'Platinum Elite',  # Old name for Platinum Elite
    }
    return mapping.get(old_level, 'Club Member')  # Default to Club Member if unknown

def migrate_membership_levels():
    """Update all users' membership_level to new naming convention"""
    app = create_app()
    
    with app.app_context():
        print("Starting membership level migration...")
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users to check")
        
        updated_count = 0
        for user in users:
            old_level = user.membership_level
            new_level = normalize_membership_level(old_level)
            
            if old_level != new_level:
                print(f"  Updating user {user.username} ({user.id}): '{old_level}' -> '{new_level}'")
                user.membership_level = new_level
                updated_count += 1
            else:
                print(f"  User {user.username} ({user.id}): '{old_level}' (already correct)")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully updated {updated_count} users")
        else:
            print("\n✓ All users already have correct membership levels")
        
        # Verify all levels are now standardized
        print("\nVerifying migration...")
        all_levels = db.session.query(User.membership_level).distinct().all()
        print("Current membership levels in database:")
        for (level,) in all_levels:
            count = User.query.filter_by(membership_level=level).count()
            print(f"  {level}: {count} user(s)")
        
        # Check for any non-standard levels
        standard_levels = {'Club Member', 'Silver Elite', 'Gold Elite', 'Diamond Elite', 'Platinum Elite'}
        found_levels = {level[0] for level in all_levels}
        non_standard = found_levels - standard_levels
        
        if non_standard:
            print(f"\n⚠ Warning: Found non-standard levels: {non_standard}")
        else:
            print("\n✓ All membership levels are now standardized!")

if __name__ == '__main__':
    migrate_membership_levels()

