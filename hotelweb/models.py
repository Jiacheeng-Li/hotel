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
        multipliers = {
            'Club Member': 1.0,
            'Silver Elite': 1.2,
            'Gold Elite': 1.5,
            'Platinum Elite': 2.0,
            'Diamond Elite': 2.5
        }
        return multipliers.get(self.membership_level, 1.0)
    
    def calculate_tier(self):
        """Calculate and update membership tier based on lifetime points OR nights stayed (whichever is higher)"""
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
        
        if new_tier != self.membership_level:
            self.membership_level = new_tier
            return True  # Tier upgraded
        return False
    
    def get_tier_benefits(self):
        """Return list of benefits for current tier"""
        benefits = {
            'Club Member': [
                'Earn points on stays',
                'Member-only rates',
                'Mobile check-in'
            ],
            'Silver Elite': [
                'All Club Member benefits',
                '1.2x points multiplier',
                'Late checkout (2 PM)',
                'Welcome amenity',
                'Priority support'
            ],
            'Gold Elite': [
                'All Silver Elite benefits',
                '1.5x points multiplier',
                'Room upgrade (subject to availability)',
                'Complimentary breakfast',
                'Priority check-in',
                'Bonus points on stays'
            ],
            'Diamond Elite': [
                'All Gold Elite benefits',
                '2x points multiplier',
                'Suite upgrade (subject to availability)',
                'Executive lounge access',
                'Guaranteed late checkout (4 PM)',
                'Dedicated concierge',
                'Premium Wi-Fi'
            ],
            'Platinum Elite': [
                'All Diamond Elite benefits',
                '2.5x points multiplier',
                'Penthouse upgrade (subject to availability)',
                'Personal travel advisor',
                'Exclusive events access',
                'Complimentary spa services',
                'Airport transfers'
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
    
    room_types = db.relationship('RoomType', backref='hotel', lazy=True)
    reviews = db.relationship('Review', backref='hotel', lazy=True, cascade="all, delete-orphan")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
