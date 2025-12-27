from datetime import datetime, date
from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Hotel, RoomType, Amenity, Booking, Brand, Review
from . import bp
from .services import search_available_roomtypes, sort_results

def award_points_for_completed_stays(user):
    """
    Checks for completed bookings for the user that haven't had points awarded yet,
    awards them, and updates user's lifetime points and tier.
    Returns total points awarded and whether a tier upgrade occurred.
    """
    from ..models import PointsTransaction
    today = date.today()
    points_awarded_total = 0
    tier_upgraded = False

    # Find bookings that have ended and points haven't been awarded
    completed_bookings = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.check_out <= today,
        Booking.status == 'CONFIRMED'
    ).all()

    for booking in completed_bookings:
        # Check if points have already been awarded for this booking
        if not PointsTransaction.query.filter_by(booking_id=booking.id, transaction_type='EARNED').first():
            points_to_award = booking.points_earned
            if points_to_award > 0:
                user.points += points_to_award
                user.lifetime_points += points_to_award
                user.nights_stayed += (booking.check_out - booking.check_in).days
                points_awarded_total += points_to_award

                # Create points transaction record
                transaction = PointsTransaction(
                    user_id=user.id,
                    booking_id=booking.id,
                    points=points_to_award,
                    transaction_type='EARNED',
                    description=f'Stay at {booking.room_type.hotel.name} - {(booking.check_out - booking.check_in).days} night(s)'
                )
                db.session.add(transaction)
                
                # Check for tier upgrade
                if user.calculate_tier():
                    tier_upgraded = True
    
    if points_awarded_total > 0:
        db.session.commit() # Commit all changes for awarded points and tier updates
    return points_awarded_total, tier_upgraded

@bp.route('/')
def index():
    cities = db.session.query(Hotel.city).distinct().all()
    cities = [c[0] for c in cities]
    brands = Brand.query.all()
    amenities = Amenity.query.all()
    # Featured Hotels (random 3) using SQLAlchemy func.random if supported, else simple slice
    featured_hotels = Hotel.query.limit(3).all()
    return render_template('main/home.html', cities=cities, brands=brands, amenities=amenities, featured_hotels=featured_hotels, today=date.today())

@bp.route('/brands')
def brands():
    brands = Brand.query.all()
    return render_template('main/brands.html', brands=brands)

@bp.route('/brand/<int:brand_id>')
def brand_detail(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    return render_template('main/brand_detail.html', brand=brand)

@bp.route('/destinations')
def destinations():
    cities = db.session.query(Hotel.city).distinct().all()
    cities_list = [c[0] for c in cities]
    # Get hotels grouped by city
    destinations_data = []
    for city_name in cities_list:
        hotels = Hotel.query.filter_by(city=city_name).limit(4).all()
        destinations_data.append({
            'city': city_name,
            'hotels': hotels,
            'image': hotels[0].image_url if hotels else ''
        })
    return render_template('main/destinations.html', destinations=destinations_data)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/search')
def search():
    print(f"DEBUG: Search params: {request.args}")
    city = request.args.get('city')
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')
    guests = int(request.args.get('guests', 1))
    rooms_needed = int(request.args.get('rooms_needed', 1))
    sort_by = request.args.get('sort_by', 'best_match')
    required_amenities = request.args.getlist('amenities')
    selected_brands = request.args.getlist('brands')

    if not city or not check_in_str or not check_out_str:
        flash('Please provide city and dates.', 'warning')
        return redirect(url_for('main.index'))

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
        return redirect(url_for('main.index'))
    
    # Catching logic errors from service
    try:
        results = search_available_roomtypes(
            city, check_in, check_out, guests, rooms_needed, required_amenities, selected_brands
        )
    except ValueError as e:
        flash(f'Search Error: {str(e)}', 'danger')
        # If possible, keep user on search page or home, redirecting to index is safe default
        return redirect(url_for('main.index'))
    
    # Group results by Hotel
    grouped_results = {}
    for item in results:
        h_id = item['hotel'].id
        if h_id not in grouped_results:
            grouped_results[h_id] = {
                'hotel': item['hotel'],
                'brand': item['brand'],
                'avg_rating': item['avg_rating'],
                'match_count': item['match_count'],
                'total_required': item['total_required'],
                'min_price': item['price'],
                'room_types': []
            }
        
        # Update min price if lower found (though usually query might be ordered, let's be safe)
        if item['price'] < grouped_results[h_id]['min_price']:
            grouped_results[h_id]['min_price'] = item['price']
            
        grouped_results[h_id]['room_types'].append(item['room_type'])
    
    final_results = list(grouped_results.values())

    # Sorting Logic for Grouped Results
    if sort_by == 'lowest_price':
        final_results.sort(key=lambda x: x['min_price'])
    elif sort_by == 'highest_rating':
        final_results.sort(key=lambda x: x['avg_rating'], reverse=True)
    else: # best_match
        final_results.sort(key=lambda x: (-x['avg_rating'], x['min_price']))
    
    all_amenities = Amenity.query.all()
    all_brands = Brand.query.all()
    
    return render_template('main/search.html', 
                           results=final_results, 
                           city=city, 
                           check_in=check_in, 
                           check_out=check_out, 
                           guests=guests,
                           rooms_needed=rooms_needed,
                           required_amenities=required_amenities,
                           selected_brands=selected_brands,
                           all_amenities=all_amenities,
                           all_brands=all_brands,
                           sort_by=sort_by,
                           today=date.today(),
                           cities=[c[0] for c in db.session.query(Hotel.city).distinct().order_by(Hotel.city).all()])

@bp.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    return render_template('main/hotel_detail.html', hotel=hotel)

@bp.route('/roomtype/<int:roomtype_id>')
def roomtype_detail(roomtype_id):
    rt = RoomType.query.get_or_404(roomtype_id)
    estimated_points_per_night = 0
    if current_user.is_authenticated:
        per_night_total = float(rt.price_per_night) * 1.15
        base_points = int(per_night_total * 10)
        multiplier = current_user.get_points_multiplier()
        estimated_points_per_night = int(base_points * multiplier)
        
    return render_template('main/roomtype_detail.html', roomtype=rt, estimated_points_per_night=estimated_points_per_night)

@bp.route('/book/<int:roomtype_id>', methods=['POST'])
@login_required
def book_room(roomtype_id):
    from ..models import PointsTransaction
    
    rt = RoomType.query.get_or_404(roomtype_id)
    
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    rooms_needed = int(request.form.get('rooms_needed', 1))
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Invalid date.', 'danger')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))

    # Strict Validation
    if check_in < date.today():
        flash('Cannot book dates in the past.', 'danger')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))

    # Calculate billing
    nights = (check_out - check_in).days
    base_rate = float(rt.price_per_night)
    subtotal = base_rate * nights * rooms_needed
    taxes = subtotal * 0.10  # 10% tax
    fees = subtotal * 0.05   # 5% service fee
    total_cost = subtotal + taxes + fees
    
    # Calculate points with tier multiplier
    # Formula: Base Points = (Room Rate × 1.15) × 10 per night
    # Then multiply by tier multiplier
    per_night_total = base_rate * 1.15  # Room rate with taxes/fees equivalent
    base_points_per_night = int(per_night_total * 10)
    multiplier = current_user.get_points_multiplier()
    points_per_night = int(base_points_per_night * multiplier)
    points_earned = points_per_night * nights * rooms_needed
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        roomtype_id=rt.id,
        check_in=check_in,
        check_out=check_out,
        rooms_count=rooms_needed,
        status='CONFIRMED',
        base_rate=base_rate,
        subtotal=subtotal,
        taxes=taxes,
        fees=fees,
        total_cost=total_cost,
        points_earned=points_earned
    )
    
    db.session.add(booking)
    db.session.flush()  # Get booking ID
    
    # Store points_earned in booking but don't award yet - points will be awarded after stay ends
    # Check for tier upgrade (based on current points, not including this booking)
    tier_upgraded = current_user.calculate_tier()
    
    db.session.commit()
    
    if tier_upgraded:
        flash(f'🎉 Congratulations! You\'ve been upgraded to {current_user.membership_level} status!', 'success')
    flash(f'Booking Confirmed! Points will be awarded after your stay ends.', 'success')
    return redirect(url_for('main.my_stays'))

@bp.route('/my/stays')
@login_required
def my_stays():
    """Display user's stays categorized by status and dates"""
    # Award points for completed stays
    points_awarded, tier_upgraded = award_points_for_completed_stays(current_user)
    if points_awarded > 0:
        flash(f'You earned {points_awarded} points from completed stays!', 'success')
    if tier_upgraded:
        flash(f'🎉 Congratulations! You\'ve been upgraded to {current_user.membership_level} status!', 'success')
    
    all_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.check_in.desc()).all()
    
    today = date.today()
    
    # Categorize bookings
    upcoming = []
    current = []
    past = []
    cancelled = []
    
    for booking in all_bookings:
        if booking.status == 'CANCELLED':
            cancelled.append(booking)
        elif booking.check_in > today:
            upcoming.append(booking)
        elif booking.check_in <= today <= booking.check_out:
            current.append(booking)
        elif booking.check_out < today:
            past.append(booking)
    
    return render_template('main/my_stays.html', 
                         upcoming=upcoming,
                         current=current,
                         past=past,
                         cancelled=cancelled,
                         today=today)

@bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
        
    booking.status = 'CANCELLED'
    # TODO: Deduct points if we want strict logic, but for now keep it simple to avoid negative balance issues.
    db.session.commit()
    
    flash('Booking cancelled.', 'info')
    return redirect(url_for('main.my_stays'))

@bp.route('/booking/<int:booking_id>/bill')
@login_required
def view_bill(booking_id):
    """Display itemized hotel bill for a booking"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    
    nights = (booking.check_out - booking.check_in).days
    return render_template('main/booking_bill.html', booking=booking, nights=nights)

@bp.route('/booking/<int:booking_id>/stay-again')
@login_required
def stay_again(booking_id):
    """Pre-fill search with same hotel for rebooking"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    
    hotel = booking.room_type.hotel
    # Suggest dates 1 year from original booking
    from datetime import timedelta
    suggested_check_in = booking.check_in + timedelta(days=365)
    suggested_check_out = booking.check_out + timedelta(days=365)
    
    # If suggested dates are in the past, use today + 7 days
    if suggested_check_in < date.today():
        suggested_check_in = date.today() + timedelta(days=7)
        suggested_check_out = suggested_check_in + (booking.check_out - booking.check_in)
    
    return redirect(url_for('main.search',
                          city=hotel.city,
                          check_in=suggested_check_in.strftime('%Y-%m-%d'),
                          check_out=suggested_check_out.strftime('%Y-%m-%d'),
                          guests=booking.room_type.capacity,
                          rooms_needed=booking.rooms_count))

@bp.route('/account')
@login_required
def account():
    """Enhanced account page with tier info and statistics"""
    # Award points for completed stays
    points_awarded, tier_upgraded = award_points_for_completed_stays(current_user)
    if points_awarded > 0:
        flash(f'You earned {points_awarded} points from completed stays!', 'success')
    if tier_upgraded:
        flash(f'🎉 Congratulations! You\'ve been upgraded to {current_user.membership_level} status!', 'success')
    
    from ..models import PointsTransaction
    from sqlalchemy import func
    import random
    
    # Generate member number if not exists
    if not current_user.member_number:
        current_user.member_number = f"{random.randint(10000000, 99999999)}"
        db.session.commit()
    
    # Calculate statistics
    total_bookings = Booking.query.filter_by(user_id=current_user.id, status='CONFIRMED').count()
    total_spent = db.session.query(func.sum(Booking.total_cost)).filter_by(user_id=current_user.id, status='CONFIRMED').scalar() or 0
    
    # All points transactions for Account Activity tab
    all_transactions = PointsTransaction.query.filter_by(user_id=current_user.id).order_by(PointsTransaction.created_at.desc()).all()
    
    # All bookings for Account Activity tab
    all_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.check_in.desc()).all()
    
    # Tier progress (points-based)
    points_to_next = current_user.points_to_next_tier()
    next_tier = current_user.next_tier_name()
    tier_benefits = current_user.get_tier_benefits()
    
    # Calculate nights-based milestone progress (separate from tier qualification)
    # Milestones at: 20, 40, 60, 100 nights
    milestone_thresholds = [20, 40, 60, 100]
    next_milestone = None
    for threshold in milestone_thresholds:
        if current_user.nights_stayed < threshold:
            next_milestone = threshold
            break
    
    if next_milestone is None:
        nights_to_next_milestone = 0
        nights_progress_percent = 100
    else:
        # Find previous milestone
        prev_milestone = 0
        for threshold in milestone_thresholds:
            if threshold < next_milestone:
                prev_milestone = threshold
        
        nights_to_next_milestone = next_milestone - current_user.nights_stayed
        range_size = next_milestone - prev_milestone
        progress_in_range = current_user.nights_stayed - prev_milestone
        nights_progress_percent = min(100, int((progress_in_range / range_size) * 100))
    
    # Calculate progress percentage for tier (points-based)
    tier_thresholds = {
        'Member': (0, 50000),
        'Silver': (50000, 100000),
        'Gold': (100000, 500000),
        'Diamond': (500000, 1000000),
        'Ambassador': (1000000, 1000000)
    }
    current_threshold = tier_thresholds.get(current_user.membership_level, (0, 50000))
    if current_user.membership_level == 'Ambassador':
        progress_percent = 100
    else:
        range_size = current_threshold[1] - current_threshold[0]
        progress_in_range = current_user.lifetime_points - current_threshold[0]
        progress_percent = min(100, int((progress_in_range / range_size) * 100))
    
    return render_template('main/account.html',
                         total_bookings=total_bookings,
                         total_spent=total_spent,
                         all_transactions=all_transactions,
                         all_bookings=all_bookings,
                         points_to_next=points_to_next,
                         next_tier=next_tier,
                         tier_benefits=tier_benefits,
                         progress_percent=progress_percent,
                         nights_to_next_milestone=nights_to_next_milestone,
                         nights_progress_percent=nights_progress_percent)

@bp.route('/account/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    from datetime import datetime
    
    current_user.username = request.form.get('username', current_user.username)
    current_user.email = request.form.get('email', current_user.email)
    current_user.phone = request.form.get('phone')
    current_user.address = request.form.get('address')
    current_user.city = request.form.get('city')
    current_user.country = request.form.get('country')
    current_user.postal_code = request.form.get('postal_code')
    
    birthday_str = request.form.get('birthday')
    if birthday_str:
        try:
            current_user.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.account'))

# Membership summary functionality has been integrated into account.html Member Benefits tab
