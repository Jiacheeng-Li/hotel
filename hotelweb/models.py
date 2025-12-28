from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association Table for Many-to-Many: RoomType <-> Amenity
roomtype_amenity = db.Table('roomtype_amenity',
    db.Column('roomtype_id', db.Integer, db.ForeignKey('room_type.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'), primary_key=True)
)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    logo_color = db.Column(db.String(20)) # Store a hex color for UI branding
    
    hotels = db.relationship('Hotel', backref='brand', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Loyalty System
    points = db.Column(db.Integer, default=0)  # Current redeemable points
    lifetime_points = db.Column(db.Integer, default=0)  # Total points earned (for tier calculation)
    nights_stayed = db.Column(db.Integer, default=0)  # Total nights stayed
    membership_level = db.Column(db.String(20), default='Club Member')  # Club Member, Silver Elite, Gold Elite, Platinum Elite, Diamond Elite
    member_number = db.Column(db.String(20), unique=True)  # Unique member ID
    
    # Tier Retention (保级系统)
    tier_earned_date = db.Column(db.Date)  # Date when current tier was first earned
    tier_expiry_date = db.Column(db.Date)  # Date when current tier expires (for retention)
    current_year_nights = db.Column(db.Integer, default=0)  # Nights stayed in current tier year
    current_year_points = db.Column(db.Integer, default=0)  # Points earned in current tier year
    
    # Profile Information
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    birthday = db.Column(db.Date)

    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_points_multiplier(self):
        """Return points multiplier based on membership tier"""
        # Normalize membership level to handle variations like "Gold" vs "Gold Elite"
        tier = self.membership_level
        if tier == 'Gold':
            tier = 'Gold Elite'
        elif tier == 'Silver':
            tier = 'Silver Elite'
        elif tier == 'Diamond':
            tier = 'Diamond Elite'
        elif tier == 'Platinum':
            tier = 'Platinum Elite'
        
        multipliers = {
            'Club Member': 1.0,
            'Silver Elite': 1.2,
            'Gold Elite': 1.5,
            'Diamond Elite': 2.0,  # Fixed: Diamond is 2.0x, not 2.5x
            'Platinum Elite': 2.5   # Fixed: Platinum is 2.5x, not 2.0x
        }
        return multipliers.get(tier, 1.0)
    
    def calculate_tier(self):
        """Calculate and update membership tier based on lifetime points OR nights stayed (whichever is higher)
        Always returns standardized tier names: Club Member, Silver Elite, Gold Elite, Diamond Elite, Platinum Elite
        """
        # Tier thresholds based on points
        points_tier = 'Club Member'
        if self.lifetime_points >= 1000000:
            points_tier = 'Platinum Elite'
        elif self.lifetime_points >= 500000:
            points_tier = 'Diamond Elite'
        elif self.lifetime_points >= 100000:
            points_tier = 'Gold Elite'
        elif self.lifetime_points >= 50000:
            points_tier = 'Silver Elite'
        
        # Tier thresholds based on nights (10 Silver Elite, 20 Gold Elite, 40 Gold Elite, 70 Diamond Elite, 200 Platinum Elite)
        nights_tier = 'Club Member'
        if self.nights_stayed >= 200:
            nights_tier = 'Platinum Elite'
        elif self.nights_stayed >= 70:
            nights_tier = 'Diamond Elite'
        elif self.nights_stayed >= 40:
            nights_tier = 'Gold Elite'
        elif self.nights_stayed >= 20:
            nights_tier = 'Gold Elite'
        elif self.nights_stayed >= 10:
            nights_tier = 'Silver Elite'
        
        # Get the higher tier (Platinum Elite > Diamond Elite > Gold Elite > Silver Elite > Club Member)
        tier_order = {'Club Member': 0, 'Silver Elite': 1, 'Gold Elite': 2, 'Diamond Elite': 3, 'Platinum Elite': 4}
        points_level = tier_order.get(points_tier, 0)
        nights_level = tier_order.get(nights_tier, 0)
        
        if points_level >= nights_level:
            new_tier = points_tier
        else:
            new_tier = nights_tier
        
        # Normalize current membership_level before comparison (handle old naming)
        current_tier = self.membership_level
        if current_tier == 'Gold':
            current_tier = 'Gold Elite'
        elif current_tier == 'Silver':
            current_tier = 'Silver Elite'
        elif current_tier == 'Diamond':
            current_tier = 'Diamond Elite'
        elif current_tier == 'Platinum':
            current_tier = 'Platinum Elite'
        elif current_tier == 'Member' or current_tier == 'Ambassador':
            current_tier = 'Club Member' if current_tier == 'Member' else 'Platinum Elite'
        
        if new_tier != current_tier:
            # Tier upgraded - update tier dates
            from datetime import date, timedelta
            today = date.today()
            self.membership_level = new_tier
            # If this is a new tier (higher than before), reset tier dates
            tier_order = {'Club Member': 0, 'Silver Elite': 1, 'Gold Elite': 2, 'Diamond Elite': 3, 'Platinum Elite': 4}
            old_level = tier_order.get(current_tier, 0)
            new_level = tier_order.get(new_tier, 0)
            if new_level > old_level:
                # Tier upgraded - set new tier dates
                self.tier_earned_date = today
                # Set expiry date to one year from today
                self.tier_expiry_date = today + timedelta(days=365)
                # Reset current year counters
                self.current_year_nights = 0
                self.current_year_points = 0
            return True  # Tier upgraded
        return False
    
    def get_tier_retention_requirements(self):
        """
        Get tier retention requirements for current tier.
        Returns dict with nights and points needed to retain tier for next year.
        """
        requirements = {
            'Club Member': {'nights': 0, 'points': 0, 'note': 'No retention required - permanent status'},
            'Silver Elite': {'nights': 10, 'points': 50000, 'note': 'Earn 10 qualifying nights OR 50,000 points per year'},
            'Gold Elite': {'nights': 20, 'points': 100000, 'note': 'Earn 20 qualifying nights OR 100,000 points per year'},
            'Diamond Elite': {'nights': 70, 'points': 500000, 'note': 'Earn 70 qualifying nights OR 500,000 points per year'},
            'Platinum Elite': {'nights': 200, 'points': 1000000, 'note': 'Earn 200 qualifying nights OR 1,000,000 points per year'}
        }
        return requirements.get(self.membership_level, requirements['Club Member'])
    
    def check_tier_retention_status(self):
        """
        Check if user meets retention requirements for current tier.
        Also handles tier expiry and downgrade if needed.
        Returns dict with status and progress info.
        """
        from datetime import date, timedelta
        requirements = self.get_tier_retention_requirements()
        
        if self.membership_level == 'Club Member':
            return {
                'status': 'permanent',
                'meets_requirement': True,
                'note': 'Club Member status is permanent'
            }
        
        # Initialize tier dates if not set
        if not self.tier_expiry_date:
            if not self.tier_earned_date:
                self.tier_earned_date = date.today()
            self.tier_expiry_date = self.tier_earned_date + timedelta(days=365)
        
        today = date.today()
        days_until_expiry = (self.tier_expiry_date - today).days
        
        # Check if tier has expired
        if days_until_expiry < 0:
            # Tier expired - check retention and downgrade if needed
            self.process_tier_expiry()
            # Recalculate after potential downgrade
            requirements = self.get_tier_retention_requirements()
            if self.membership_level == 'Club Member':
                return {
                    'status': 'permanent',
                    'meets_requirement': True,
                    'note': 'Club Member status is permanent'
                }
        
        # Check if user meets retention requirement (nights OR points)
        meets_nights = self.current_year_nights >= requirements['nights']
        meets_points = self.current_year_points >= requirements['points']
        meets_requirement = meets_nights or meets_points
        
        return {
            'status': 'active' if meets_requirement else 'at_risk',
            'meets_requirement': meets_requirement,
            'expiry_date': self.tier_expiry_date,
            'days_until_expiry': days_until_expiry,
            'current_nights': self.current_year_nights,
            'current_points': self.current_year_points,
            'required_nights': requirements['nights'],
            'required_points': requirements['points'],
            'note': requirements['note']
        }
    
    def process_tier_expiry(self):
        """
        Process tier expiry: check if retention requirements are met,
        and downgrade if not. Reset counters for new tier year if retained.
        """
        from datetime import date, timedelta
        requirements = self.get_tier_retention_requirements()
        
        # Check if retention requirement is met
        meets_nights = self.current_year_nights >= requirements['nights']
        meets_points = self.current_year_points >= requirements['points']
        meets_requirement = meets_nights or meets_points
        
        if meets_requirement:
            # Retention requirement met - extend tier for another year
            self.tier_earned_date = date.today()
            self.tier_expiry_date = date.today() + timedelta(days=365)
            # Reset counters for new tier year
            self.current_year_nights = 0
            self.current_year_points = 0
        else:
            # Retention requirement not met - downgrade based on lifetime stats
            old_tier = self.membership_level
            # Recalculate tier based on lifetime points/nights
            self.calculate_tier()
            new_tier = self.membership_level
            
            if old_tier != new_tier:
                # Tier was downgraded - reset dates and counters
                self.tier_earned_date = date.today()
                self.tier_expiry_date = date.today() + timedelta(days=365)
                self.current_year_nights = 0
                self.current_year_points = 0
    
    def get_tier_benefits(self):
        """Return list of benefits for current tier - matches comparison table"""
        benefits = {
            'Club Member': [
                'Earn Points on Stays',
                'Club Member-only Rates',
                'Mobile Check-in',
                '1.0x Points Multiplier'
            ],
            'Silver Elite': [
                'Earn Points on Stays',
                'Club Member-only Rates',
                'Mobile Check-in',
                '1.2x Points Multiplier',
                'Late Checkout (2 PM)',
                'Welcome Amenity',
                'Priority Support'
            ],
            'Gold Elite': [
                'Earn Points on Stays',
                'Club Member-only Rates',
                'Mobile Check-in',
                '1.5x Points Multiplier',
                'Late Checkout (2 PM)',
                'Welcome Amenity',
                'Priority Support',
                'Room Upgrade (Subject to availability)',
                'Complimentary Breakfast',
                'Priority Check-in'
            ],
            'Diamond Elite': [
                'Earn Points on Stays',
                'Club Member-only Rates',
                'Mobile Check-in',
                '2.0x Points Multiplier',
                'Late Checkout (4 PM)',
                'Welcome Amenity',
                'Priority Support',
                'Suite Upgrade (Subject to availability)',
                'Complimentary Breakfast',
                'Priority Check-in',
                'Executive Lounge Access',
                'Dedicated Concierge'
            ],
            'Platinum Elite': [
                'Earn Points on Stays',
                'Club Member-only Rates',
                'Mobile Check-in',
                '2.5x Points Multiplier',
                'Late Checkout (4 PM)',
                'Welcome Amenity',
                'Priority Support',
                'Penthouse Upgrade (Subject to availability)',
                'Complimentary Breakfast',
                'Priority Check-in',
                'Executive Lounge Access',
                'Dedicated Concierge',
                'Personal Travel Advisor',
                'Exclusive Events Access',
                'Complimentary Spa Services',
                'Airport Transfers'
            ]
        }
        return benefits.get(self.membership_level, benefits['Club Member'])
    
    def points_to_next_tier(self):
        """Calculate points needed to reach next tier"""
        thresholds = {
            'Club Member': 50000,
            'Silver Elite': 100000,
            'Gold Elite': 500000,
            'Diamond Elite': 1000000,
            'Platinum Elite': None  # Already at top tier
        }
        next_threshold = thresholds.get(self.membership_level)
        if next_threshold is None:
            return 0
        return max(0, next_threshold - self.lifetime_points)
    
    def next_tier_name(self):
        """Return name of next tier"""
        tiers = {
            'Club Member': 'Silver Elite',
            'Silver Elite': 'Gold Elite',
            'Gold Elite': 'Diamond Elite',
            'Diamond Elite': 'Platinum Elite',
            'Platinum Elite': 'Platinum Elite'
        }
        return tiers.get(self.membership_level, 'Silver Elite')

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=True) # Check if can be null for migration
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    
    # Stars & Map
    stars = db.Column(db.Integer, default=4)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Breakfast pricing (varies by hotel star rating: 5-star=$50, 4-star=$40, 3-star=$30, 2-star=$20, 1-star=$10)
    breakfast_price = db.Column(db.Numeric(10, 2), default=25.00)
    
    room_types = db.relationship('RoomType', backref='hotel', lazy=True)
    reviews = db.relationship('Review', backref='hotel', lazy=True, cascade="all, delete-orphan")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)  # Optional: link to specific booking
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    booking = db.relationship('Booking', backref='review', lazy=True)

class RoomType(db.Model):
    __tablename__ = 'room_type'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    inventory = db.Column(db.Integer, default=1, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))

    amenities = db.relationship('Amenity', secondary=roomtype_amenity, lazy='subquery',
        backref=db.backref('room_types', lazy=True))
    
    bookings = db.relationship('Booking', backref='room_type', lazy=True)

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) 

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    roomtype_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    rooms_count = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default='CONFIRMED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Billing fields
    base_rate = db.Column(db.Numeric(10, 2), default=0)  # Room rate per night
    subtotal = db.Column(db.Numeric(10, 2), default=0)  # base_rate * nights * rooms
    taxes = db.Column(db.Numeric(10, 2), default=0)  # Tax amount
    fees = db.Column(db.Numeric(10, 2), default=0)  # Service fees
    total_cost = db.Column(db.Numeric(10, 2), default=0)  # Final total
    
    # Points tracking
    points_earned = db.Column(db.Integer, default=0)  # Points earned from this booking
    points_used = db.Column(db.Integer, default=0)  # Points used to pay for this booking
    
    # Breakfast option
    breakfast_included = db.Column(db.Boolean, default=False)
    breakfast_price_per_room = db.Column(db.Numeric(10, 2), default=0)  # Breakfast price per room per stay
    breakfast_voucher_used = db.Column(db.Integer, db.ForeignKey('milestone_reward.id'), nullable=True)  # Which breakfast voucher was used
    
    # Payment method
    payment_method = db.Column(db.String(20), default='pay_now')  # pay_now, pay_at_hotel, points
    
    user = db.relationship('User', backref='bookings', lazy=True)

class PointsTransaction(db.Model):
    """Track all points activity for transparency"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)
    points = db.Column(db.Integer, nullable=False)  # Positive for earned, negative for redeemed
    transaction_type = db.Column(db.String(20), nullable=False)  # EARNED, REDEEMED, EXPIRED, BONUS
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='points_transactions', lazy=True)
    booking = db.relationship('Booking', backref='points_transaction', lazy=True)

class MilestoneReward(db.Model):
    """Track milestone rewards earned by users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    milestone_nights = db.Column(db.Integer, nullable=False)  # The milestone threshold (20, 30, 40, etc.)
    reward_type = db.Column(db.String(20), nullable=False)  # 'points' or 'breakfast'
    reward_value = db.Column(db.Integer)  # For points: 5000, For breakfast: 2 (number of breakfasts)
    breakfasts_used = db.Column(db.Integer, default=0)  # Number of breakfasts used from this reward
    claimed_at = db.Column(db.DateTime)  # When user selected their reward
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='milestone_rewards', lazy=True)
    
    def get_available_breakfasts(self):
        """Get number of available breakfasts from this reward"""
        if self.reward_type == 'breakfast':
            return max(0, self.reward_value - self.breakfasts_used)
        return 0
