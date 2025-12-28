from datetime import date, timedelta
from sqlalchemy import and_, or_, func, desc
from ..extensions import db
from ..models import RoomType, Booking, Hotel, Amenity, Brand, Review

def search_available_roomtypes(city, check_in, check_out, guests, rooms_needed=1, required_amenity_ids=None, brand_ids=None):
    """
    Enhanced search algorithm with Brand filtering and strict checks.
    """
    if required_amenity_ids is None:
        required_amenity_ids = []
    
    # Validation
    today = date.today()
    # Relaxed check: allow yesterday to handle timezone edge cases
    if check_in < today - timedelta(days=1):
        raise ValueError(f"Check-in date cannot be in the past. (Received: {check_in}, Today: {today})")
    
    if check_in >= check_out:
        raise ValueError("Check-out must be after check-in.")

    # 1. Base Query
    query = RoomType.query.join(Hotel).filter(
        Hotel.city == city,
        RoomType.capacity >= guests
    )
    
    # Brand Filter
    if brand_ids:
        query = query.filter(Hotel.brand_id.in_(brand_ids))
    
    room_types = query.all()
    results = []

    for rt in room_types:
        # 2. Check Inventory (Availability)
        overlapping_bookings = Booking.query.filter(
            Booking.roomtype_id == rt.id,
            Booking.status == 'CONFIRMED',
            or_(
                and_(Booking.check_in < check_out, Booking.check_out > check_in)
            )
        ).all()
        
        booked_count = sum(b.rooms_count for b in overlapping_bookings)
        available_count = rt.inventory - booked_count
        
        if available_count < rooms_needed:
            continue 
        
        # 3. Amenity Matching
        rt_amenity_ids = {a.id for a in rt.amenities}
        req_amenity_ids_set = set(map(int, required_amenity_ids))
        
        if not required_amenity_ids:
            # If no specific amenities required, show total count available
            match_count = len(rt.amenities)
            total_required = 0 # Interpreted as 'All' or 'N/A' in template
        else:
            if not req_amenity_ids_set.issubset(rt_amenity_ids):
                continue
            matched_amenities = [a for a in rt.amenities if a.id in req_amenity_ids_set]
            match_count = len(matched_amenities)
            total_required = len(req_amenity_ids_set)
        
        # Calculate Hotel Average Rating
        avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.hotel_id == rt.hotel.id).scalar() or 0
        
        results.append({
            'room_type': rt,
            'hotel': rt.hotel,
            'brand': rt.hotel.brand,
            'match_count': match_count,
            'total_required': total_required,
            'price': rt.price_per_night,
            'available': available_count,
            'avg_rating': round(avg_rating, 1)
        })

    return results

def sort_results(results, sort_by='best_match'):
    if sort_by == 'lowest_price':
        return sorted(results, key=lambda x: x['price'])
    elif sort_by == 'highest_price':
        return sorted(results, key=lambda x: x['price'], reverse=True)
    elif sort_by == 'highest_rating':
        return sorted(results, key=lambda x: x['avg_rating'], reverse=True)
    elif sort_by == 'lowest_rating':
        return sorted(results, key=lambda x: x['avg_rating'])
    elif sort_by == 'highest_stars':
        return sorted(results, key=lambda x: x['hotel'].stars if hasattr(x['hotel'], 'stars') else 0, reverse=True)
    elif sort_by == 'lowest_stars':
        return sorted(results, key=lambda x: x['hotel'].stars if hasattr(x['hotel'], 'stars') else 0)
    elif sort_by == 'best_match':
        # Combined Score: Rating * 20% + Price (normalized inverse) ... simplified
        # Sort by Rating desc, then price asc
        return sorted(results, key=lambda x: (-x['avg_rating'], x['price']))
    
    return results

def calculate_points_earned(amount, membership_level):
    """
    Calculate points earned based on membership level.
    Uses standardized tier names: Club Member, Silver Elite, Gold Elite, Diamond Elite, Platinum Elite
    """
    # Normalize membership level to handle any variations
    tier = membership_level
    if tier == 'Gold':
        tier = 'Gold Elite'
    elif tier == 'Silver':
        tier = 'Silver Elite'
    elif tier == 'Diamond':
        tier = 'Diamond Elite'
    elif tier == 'Platinum':
        tier = 'Platinum Elite'
    elif tier == 'Member' or tier == 'Ambassador':
        tier = 'Club Member' if tier == 'Member' else 'Platinum Elite'
    
    # Points per $1 based on tier multiplier
    # Base: 10 points per $1, then multiplied by tier multiplier
    multipliers = {
        'Club Member': 10,      # 1.0x = 10 points per $1
        'Silver Elite': 12,     # 1.2x = 12 points per $1
        'Gold Elite': 15,       # 1.5x = 15 points per $1
        'Diamond Elite': 20,    # 2.0x = 20 points per $1
        'Platinum Elite': 25    # 2.5x = 25 points per $1
    }
    multiplier = multipliers.get(tier, 10)
    return int(amount * multiplier)
