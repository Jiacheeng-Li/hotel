from datetime import datetime, date
from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Hotel, RoomType, Amenity, Booking, Brand, Review, PointsTransaction, MilestoneReward
from . import bp
from .services import search_available_roomtypes, sort_results

def award_points_for_completed_stays(user):
    """
    Checks for completed bookings for the user that haven't had points awarded yet,
    awards them, and updates user's lifetime points and tier.
    Returns total points awarded and whether a tier upgrade occurred.
    """
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
        nights = (booking.check_out - booking.check_in).days
        
        # Check if nights have already been counted for this booking
        # We check if there's an EARNED transaction (for points bookings) or if booking has been processed
        existing_earned_transaction = PointsTransaction.query.filter_by(booking_id=booking.id, transaction_type='EARNED').first()
        
        # For points-paid bookings (points_used > 0), we still need to count nights even if no points were earned
        # Check if nights have been counted by looking for any transaction with this booking_id
        nights_already_counted = PointsTransaction.query.filter_by(booking_id=booking.id).first() is not None
        
        if not nights_already_counted:
            # Count nights for all completed bookings (including points-paid bookings)
            user.nights_stayed += nights
            
            # Update current tier year stats for retention tracking
            # Only count if booking is within current tier year (tier_earned_date to tier_expiry_date)
            if user.tier_earned_date and user.tier_expiry_date:
                if booking.check_out >= user.tier_earned_date and booking.check_out <= user.tier_expiry_date:
                    user.current_year_nights += nights
            elif user.tier_earned_date:
                # If only tier_earned_date is set, count bookings after that date
                if booking.check_out >= user.tier_earned_date:
                    user.current_year_nights += nights
        
        # Award points if not already awarded and points were earned
        if not existing_earned_transaction:
            points_to_award = booking.points_earned
            if points_to_award > 0:
                # Update lifetime stats for points
                user.points += points_to_award
                user.lifetime_points += points_to_award
                points_awarded_total += points_to_award
                
                # Update current tier year stats for points
                if user.tier_earned_date and user.tier_expiry_date:
                    if booking.check_out >= user.tier_earned_date and booking.check_out <= user.tier_expiry_date:
                        user.current_year_points += points_to_award
                elif user.tier_earned_date:
                    if booking.check_out >= user.tier_earned_date:
                        user.current_year_points += points_to_award

                # Create points transaction record
                transaction = PointsTransaction(
                    user_id=user.id,
                    booking_id=booking.id,
                    points=points_to_award,
                    transaction_type='EARNED',
                    description=f'Stay at {booking.room_type.hotel.name} - {nights} night(s)'
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
    from datetime import timedelta
    tomorrow = date.today() + timedelta(days=1)
    return render_template('main/home.html', cities=cities, brands=brands, amenities=amenities, featured_hotels=featured_hotels, today=date.today(), tomorrow=tomorrow)

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
    # Get hotels grouped by city - limit to 3 for display
    destinations_data = []
    for city_name in cities_list:
        hotels = Hotel.query.filter_by(city=city_name).limit(3).all()
        destinations_data.append({
            'city': city_name,
            'hotels': hotels,
            'image': hotels[0].image_url if hotels else ''
        })
    return render_template('main/destinations.html', destinations=destinations_data)

@bp.route('/city/<city_name>')
def city_hotels(city_name):
    """Display all hotels in a specific city"""
    hotels = Hotel.query.filter_by(city=city_name).all()
    if not hotels:
        flash(f'No hotels found in {city_name}.', 'warning')
        return redirect(url_for('main.destinations'))
    
    return render_template('main/city_hotels.html', city=city_name, hotels=hotels)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/sustainability')
def sustainability():
    return render_template('main/sustainability.html')

@bp.route('/careers')
def careers():
    return render_template('main/careers.html')

@bp.route('/contact')
def contact():
    return render_template('main/contact.html')

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
                'max_price': item['price'],
                'room_types': []
            }
        
        # Update min and max price
        if item['price'] < grouped_results[h_id]['min_price']:
            grouped_results[h_id]['min_price'] = item['price']
        if item['price'] > grouped_results[h_id]['max_price']:
            grouped_results[h_id]['max_price'] = item['price']
            
        grouped_results[h_id]['room_types'].append(item['room_type'])
    
    final_results = list(grouped_results.values())

    # Sorting Logic for Grouped Results
    if sort_by == 'lowest_price':
        final_results.sort(key=lambda x: x['min_price'])
    elif sort_by == 'highest_price':
        final_results.sort(key=lambda x: x['max_price'], reverse=True)
    elif sort_by == 'highest_rating':
        final_results.sort(key=lambda x: x['avg_rating'], reverse=True)
    elif sort_by == 'lowest_rating':
        final_results.sort(key=lambda x: x['avg_rating'])
    elif sort_by == 'highest_stars':
        final_results.sort(key=lambda x: x['hotel'].stars if x['hotel'].stars else 0, reverse=True)
    elif sort_by == 'lowest_stars':
        final_results.sort(key=lambda x: x['hotel'].stars if x['hotel'].stars else 0)
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
    
    # Detect where user came from (via referrer or URL params)
    referrer = request.referrer
    from_source = request.args.get('from')  # from=search, from=brand, from=destinations
    
    # Determine breadcrumb context
    breadcrumb_context = {
        'from_search': False,
        'from_brand': False,
        'from_destinations': False,
        'from_city': False,
        'search_params': {},
        'brand_id': None,
        'city_name': None
    }
    
    if from_source == 'search' or (not from_source and referrer and '/search' in referrer):
        breadcrumb_context['from_search'] = True
        # Get search params from URL params first (more reliable)
        if request.args.get('check_in') or request.args.get('check_out'):
            breadcrumb_context['search_params'] = {}
            if request.args.get('check_in'):
                breadcrumb_context['search_params']['check_in'] = request.args.get('check_in')
            if request.args.get('check_out'):
                breadcrumb_context['search_params']['check_out'] = request.args.get('check_out')
        elif referrer:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(referrer)
            search_params = parse_qs(parsed.query)
            breadcrumb_context['search_params'] = {k: v[0] if v else '' for k, v in search_params.items()}
    elif from_source == 'city' or (not from_source and referrer and '/city/' in referrer):
        breadcrumb_context['from_city'] = True
        # Get city name from URL param or referrer
        city_name = request.args.get('city_name')
        if city_name:
            breadcrumb_context['city_name'] = city_name
        elif referrer and '/city/' in referrer:
            from urllib.parse import urlparse
            parsed = urlparse(referrer)
            # Extract city name from /city/city_name URL
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 3 and path_parts[1] == 'city':
                breadcrumb_context['city_name'] = path_parts[2]
        # Fallback to hotel's city if not found
        if not breadcrumb_context['city_name']:
            breadcrumb_context['city_name'] = hotel.city
    elif from_source == 'brand' or (not from_source and referrer and '/brand/' in referrer):
        breadcrumb_context['from_brand'] = True
        breadcrumb_context['brand_id'] = hotel.brand_id
    elif from_source == 'destinations' or (not from_source and referrer and '/destinations' in referrer):
        breadcrumb_context['from_destinations'] = True
    
    # Get recommended hotels (same city, same brand, or same stars, excluding current hotel)
    recommended_hotels = []
    
    # Priority 1: Same brand and same city
    same_brand_city = Hotel.query.filter(
        Hotel.id != hotel_id,
        Hotel.brand_id == hotel.brand_id,
        Hotel.city == hotel.city
    ).limit(3).all()
    recommended_hotels.extend(same_brand_city)
    
    # Priority 2: Same city and same stars (if we don't have enough)
    if len(recommended_hotels) < 3:
        same_city_stars = Hotel.query.filter(
            Hotel.id != hotel_id,
            Hotel.city == hotel.city,
            Hotel.stars == hotel.stars,
            ~Hotel.id.in_([h.id for h in recommended_hotels])
        ).limit(3 - len(recommended_hotels)).all()
        recommended_hotels.extend(same_city_stars)
    
    # Priority 3: Same city (if we still don't have enough)
    if len(recommended_hotels) < 3:
        same_city = Hotel.query.filter(
            Hotel.id != hotel_id,
            Hotel.city == hotel.city,
            ~Hotel.id.in_([h.id for h in recommended_hotels])
        ).limit(3 - len(recommended_hotels)).all()
        recommended_hotels.extend(same_city)
    
    # Priority 4: Same brand (if we still don't have enough)
    if len(recommended_hotels) < 3:
        same_brand = Hotel.query.filter(
            Hotel.id != hotel_id,
            Hotel.brand_id == hotel.brand_id,
            ~Hotel.id.in_([h.id for h in recommended_hotels])
        ).limit(3 - len(recommended_hotels)).all()
        recommended_hotels.extend(same_brand)
    
    # Limit to 3 hotels
    recommended_hotels = recommended_hotels[:3]
    
    return render_template('main/hotel_detail.html', 
                          hotel=hotel, 
                          recommended_hotels=recommended_hotels,
                          breadcrumb=breadcrumb_context)

@bp.route('/roomtype/<int:roomtype_id>')
def roomtype_detail(roomtype_id):
    rt = RoomType.query.get_or_404(roomtype_id)
    estimated_points_per_night = 0
    if current_user.is_authenticated:
        per_night_total = float(rt.price_per_night) * 1.15
        base_points = int(per_night_total * 10)
        multiplier = current_user.get_points_multiplier()
        estimated_points_per_night = int(base_points * multiplier)
    
    # Detect where user came from (via referrer or URL params)
    referrer = request.referrer
    from_source = request.args.get('from')
    
    # Determine breadcrumb context
    breadcrumb_context = {
        'from_search': False,
        'from_brand': False,
        'from_destinations': False,
        'from_city': False,
        'search_params': {},
        'brand_id': None,
        'city_name': None
    }
    
    # Check if came from hotel detail page (check referrer chain)
    if referrer and '/hotel/' in referrer:
        # Try to detect the original source - check if there's a from parameter in the referrer
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(referrer)
        ref_params = parse_qs(parsed.query)
        if 'from' in ref_params:
            from_source = ref_params['from'][0]
            # If from search, also extract check_in and check_out from referrer params
            if from_source == 'search':
                search_params = {}
                if 'check_in' in ref_params:
                    search_params['check_in'] = ref_params['check_in'][0]
                if 'check_out' in ref_params:
                    search_params['check_out'] = ref_params['check_out'][0]
                if search_params:
                    breadcrumb_context['search_params'] = search_params
            elif from_source == 'city' and 'city_name' in ref_params:
                breadcrumb_context['city_name'] = ref_params['city_name'][0]
        else:
            # Fallback to checking referrer path
            if '/search' in referrer:
                from_source = 'search'
                search_params = parse_qs(parsed.query)
                breadcrumb_context['search_params'] = {k: v[0] if v else '' for k, v in search_params.items()}
            elif '/brand/' in referrer:
                from_source = 'brand'
            elif '/city/' in referrer:
                from_source = 'city'
                path_parts = parsed.path.split('/')
                if len(path_parts) >= 3 and path_parts[1] == 'city':
                    breadcrumb_context['city_name'] = path_parts[2]
            elif '/destinations' in referrer:
                from_source = 'destinations'
    
    if from_source:
        # Process from_source parameter
        if from_source == 'search':
            breadcrumb_context['from_search'] = True
            # Try to get search params from referrer if available (should already be set above)
            if not breadcrumb_context['search_params'] and referrer and '/search' in referrer:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(referrer)
                search_params = parse_qs(parsed.query)
                breadcrumb_context['search_params'] = {k: v[0] if v else '' for k, v in search_params.items()}
        elif from_source == 'city':
            breadcrumb_context['from_city'] = True
            # Get city_name from URL param if not already set
            if not breadcrumb_context['city_name']:
                breadcrumb_context['city_name'] = request.args.get('city_name') or rt.hotel.city
        elif from_source == 'brand':
            breadcrumb_context['from_brand'] = True
            breadcrumb_context['brand_id'] = rt.hotel.brand_id
        elif from_source == 'destinations':
            breadcrumb_context['from_destinations'] = True
    
    # Get default dates from search params or URL params, or use today/tomorrow
    default_check_in = request.args.get('check_in', '')
    default_check_out = request.args.get('check_out', '')
    
    # If coming from search, try to get dates from search_params
    if breadcrumb_context['from_search'] and breadcrumb_context['search_params']:
        if not default_check_in and 'check_in' in breadcrumb_context['search_params']:
            default_check_in = breadcrumb_context['search_params']['check_in']
        if not default_check_out and 'check_out' in breadcrumb_context['search_params']:
            default_check_out = breadcrumb_context['search_params']['check_out']
    
    # Set default dates if not provided: today to tomorrow
    if not default_check_in:
        default_check_in = date.today().strftime('%Y-%m-%d')
    if not default_check_out:
        from datetime import timedelta
        default_check_out = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Breakfast price from hotel (varies by hotel star rating)
    breakfast_price_per_room = float(rt.hotel.breakfast_price)
    
    return render_template('main/roomtype_detail.html', 
                         roomtype=rt, 
                         estimated_points_per_night=estimated_points_per_night, 
                         today=date.today(),
                         breadcrumb=breadcrumb_context,
                         default_check_in=default_check_in,
                         default_check_out=default_check_out,
                         breakfast_price_per_room=breakfast_price_per_room)

@bp.route('/book/<int:roomtype_id>/confirm')
@login_required
def booking_confirm(roomtype_id):
    """Display booking confirmation page with price breakdown and payment options"""
    rt = RoomType.query.get_or_404(roomtype_id)
    
    # Get booking parameters from query string
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')
    rooms_needed = int(request.args.get('rooms_needed', 1))
    breakfast_included = request.args.get('breakfast_included') == '1'
    breakfast_voucher_id = request.args.get('breakfast_voucher_id')  # For pre-selection
    
    if not check_in_str or not check_out_str:
        flash('Please select check-in and check-out dates.', 'warning')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Invalid date format.', 'danger')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))
    
    # Validation
    if check_in < date.today():
        flash('Cannot book dates in the past.', 'danger')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))
    
    if check_out <= check_in:
        flash('Check-out date must be after check-in date.', 'danger')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))
    
    # Calculate billing
    nights = (check_out - check_in).days
    base_rate = float(rt.price_per_night)
    subtotal = base_rate * nights * rooms_needed
    
    # Query available breakfast vouchers (milestone rewards with unused breakfasts)
    available_breakfast_vouchers = []
    breakfast_rewards = MilestoneReward.query.filter_by(
        user_id=current_user.id,
        reward_type='breakfast'
    ).all()
    
    for reward in breakfast_rewards:
        available = reward.get_available_breakfasts()
        if available > 0:
            available_breakfast_vouchers.append({
                'id': reward.id,
                'milestone_nights': reward.milestone_nights,
                'available': available,
                'total': reward.reward_value
            })
    
    # Breakfast pricing (per room per stay) - from hotel database
    breakfast_price_per_room = float(rt.hotel.breakfast_price)
    breakfast_voucher_used = None
    
    # Check if user wants to use a breakfast voucher
    if breakfast_included and breakfast_voucher_id:
        try:
            breakfast_voucher_id_int = int(breakfast_voucher_id)
            voucher = MilestoneReward.query.filter_by(
                id=breakfast_voucher_id_int,
                user_id=current_user.id,
                reward_type='breakfast'
            ).first()
            
            if voucher and voucher.get_available_breakfasts() >= rooms_needed:
                breakfast_voucher_used = voucher
                breakfast_total = 0  # Free with voucher
            else:
                breakfast_total = breakfast_price_per_room * rooms_needed
        except (ValueError, TypeError):
            breakfast_total = breakfast_price_per_room * rooms_needed
    else:
        breakfast_total = breakfast_price_per_room * rooms_needed if breakfast_included else 0
    
    # Calculate taxes and fees on base rate only (breakfast may be taxed separately in real system)
    taxes = subtotal * 0.10  # 10% tax
    fees = subtotal * 0.05   # 5% service fee
    total_cost = subtotal + taxes + fees
    final_total = total_cost + breakfast_total
    
    # Calculate estimated points (for display only, actual points calculated after payment)
    # Formula: 1 dollar = 10 base points, then multiply by tier multiplier
    # Points are calculated based on actual payment amount (excluding points payment)
    per_night_total = base_rate * 1.15  # Room rate with taxes/fees equivalent
    base_points_per_night = int(per_night_total * 10)  # 10 points per $1
    multiplier = current_user.get_points_multiplier()
    points_per_night = int(base_points_per_night * multiplier)
    points_earned = points_per_night * nights * rooms_needed
    
    return render_template('main/booking_confirm.html',
                         roomtype=rt,
                         check_in=check_in,
                         check_out=check_out,
                         rooms_needed=rooms_needed,
                         nights=nights,
                         base_rate=base_rate,
                         subtotal=subtotal,
                         taxes=taxes,
                         fees=fees,
                         total_cost=total_cost,
                         breakfast_included=breakfast_included,
                         breakfast_total=breakfast_total,
                         breakfast_price_per_room=breakfast_price_per_room,
                         breakfast_voucher_used=breakfast_voucher_used,
                         final_total=final_total,
                         points_earned=points_earned,
                         available_breakfast_vouchers=available_breakfast_vouchers)

@bp.route('/book/<int:roomtype_id>', methods=['POST'])
@login_required
def book_room(roomtype_id):
    rt = RoomType.query.get_or_404(roomtype_id)
    
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    rooms_needed = int(request.form.get('rooms_needed', 1))
    payment_method = request.form.get('payment_method', 'pay_now')
    breakfast_included = request.form.get('breakfast_included') == '1'
    breakfast_voucher_id = request.form.get('breakfast_voucher_id')  # ID of breakfast voucher to use
    
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
    
    if check_out <= check_in:
        flash('Check-out date must be after check-in date.', 'danger')
        return redirect(url_for('main.roomtype_detail', roomtype_id=roomtype_id))

    # Calculate billing
    nights = (check_out - check_in).days
    base_rate = float(rt.price_per_night)
    subtotal = base_rate * nights * rooms_needed
    
    # Breakfast pricing and voucher handling
    # Breakfast pricing - from hotel database
    breakfast_price_per_room = float(rt.hotel.breakfast_price)
    breakfast_voucher_used_id = None
    breakfast_total = 0
    
    if breakfast_included:
        # Check if user wants to use a breakfast voucher
        if breakfast_voucher_id:
            try:
                breakfast_voucher_id = int(breakfast_voucher_id)
                voucher = MilestoneReward.query.filter_by(
                    id=breakfast_voucher_id,
                    user_id=current_user.id,
                    reward_type='breakfast'
                ).first()
                
                if voucher and voucher.get_available_breakfasts() >= rooms_needed:
                    # Use breakfast voucher - breakfast is free
                    breakfast_voucher_used_id = voucher.id
                    breakfast_total = 0
                    # Update voucher usage
                    voucher.breakfasts_used += rooms_needed
                else:
                    # Voucher not available or insufficient, charge for breakfast
                    breakfast_total = breakfast_price_per_room * rooms_needed
            except (ValueError, TypeError):
                # Invalid voucher ID, charge for breakfast
                breakfast_total = breakfast_price_per_room * rooms_needed
        else:
            # No voucher selected, charge for breakfast
            breakfast_total = breakfast_price_per_room * rooms_needed
    
    taxes = subtotal * 0.10  # 10% tax
    fees = subtotal * 0.05   # 5% service fee
    total_cost = subtotal + taxes + fees
    final_total = total_cost + breakfast_total
    
    # Handle points payment
    points_used = 0
    points_transaction = None
    if payment_method == 'points':
        points_needed = int(final_total * 100)  # 100 points = $1
        if current_user.points < points_needed:
            flash(f'Insufficient points. You have {current_user.points:,} points but need {points_needed:,} points.', 'danger')
            return redirect(url_for('main.booking_confirm', roomtype_id=roomtype_id, 
                                  check_in=check_in_str, check_out=check_out_str, 
                                  rooms_needed=rooms_needed, breakfast_included='1' if breakfast_included else '0'))
        points_used = points_needed
        current_user.points -= points_used
        # Record points transaction (will add booking_id after booking is created)
        points_transaction = PointsTransaction(
            user_id=current_user.id,
            points=-points_used,
            transaction_type='REDEEMED',
            description=f'Payment for booking at {rt.hotel.name}'
        )
        db.session.add(points_transaction)
        db.session.flush()  # Get transaction ID
        final_total = 0  # Fully paid with points
    
    # Calculate points earned based on ACTUAL PAYMENT AMOUNT
    # Formula: 1 dollar = 10 base points, then multiply by tier multiplier
    # Important: Points are NOT earned on amounts paid with points
    # If fully paid with points (final_total = 0), no points are earned
    if final_total > 0:
        # Calculate based on actual payment amount (excluding points payment)
        # Use per-night rate with taxes/fees equivalent
        per_night_total = base_rate * 1.15  # Room rate with taxes/fees equivalent
        base_points_per_night = int(per_night_total * 10)  # 10 points per $1
        multiplier = current_user.get_points_multiplier()
        points_per_night = int(base_points_per_night * multiplier)
        points_earned = points_per_night * nights * rooms_needed
    else:
        # Fully paid with points - no points earned
        points_earned = 0
    
    # Create booking
    booking = Booking(
        breakfast_included=breakfast_included,
        breakfast_price_per_room=breakfast_price_per_room if breakfast_included and not breakfast_voucher_used_id else 0,
        breakfast_voucher_used=breakfast_voucher_used_id,
        points_used=points_used,
        payment_method=payment_method,
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
        total_cost=final_total,  # Include breakfast in total
        points_earned=points_earned
    )
    
    db.session.add(booking)
    db.session.flush()  # Get booking ID
    
    # Update points transaction with booking_id if it was a points payment
    if points_used > 0:
        points_transaction.booking_id = booking.id
    
    # Store points_earned in booking but don't award yet - points will be awarded after stay ends
    # Check for tier upgrade (based on current points, not including this booking)
    tier_upgraded = current_user.calculate_tier()
    
    db.session.commit()
    
    # Payment method message
    payment_msg = "Payment will be processed now." if payment_method == 'pay_now' else "Payment will be collected at the hotel upon arrival."
    
    if tier_upgraded:
        flash(f'🎉 Congratulations! You\'ve been upgraded to {current_user.membership_level} status!', 'success')
    flash(f'Booking Confirmed! {payment_msg} Points will be awarded after your stay ends.', 'success')
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
    
    # Sort upcoming by check-in date (ascending - nearest first)
    upcoming.sort(key=lambda b: b.check_in)
    
    # Check which bookings already have reviews
    reviewed_booking_ids = set()
    for booking in past:
        existing_review = Review.query.filter_by(booking_id=booking.id, user_id=current_user.id).first()
        if existing_review:
            reviewed_booking_ids.add(booking.id)
    
    return render_template('main/my_stays.html', 
                         upcoming=upcoming,
                         current=current,
                         past=past,
                         cancelled=cancelled,
                         today=today,
                         reviewed_booking_ids=reviewed_booking_ids)

@bp.route('/booking/<int:booking_id>/review', methods=['GET', 'POST'])
@login_required
def write_review(booking_id):
    """Write a review for a completed booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify ownership
    if booking.user_id != current_user.id:
        abort(403)
    
    # Check if booking is completed
    if booking.check_out > date.today():
        flash('You can only review completed stays.', 'warning')
        return redirect(url_for('main.my_stays'))
    
    # Check if already reviewed (for editing)
    existing_review = Review.query.filter_by(booking_id=booking_id, user_id=current_user.id).first()
    
    hotel = booking.room_type.hotel
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        
        # Validation
        if not rating:
            flash('Please select a rating.', 'danger')
            return render_template('main/write_review.html', booking=booking, hotel=hotel, existing_review=existing_review)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            flash('Invalid rating. Please select a rating between 1 and 5.', 'danger')
            return render_template('main/write_review.html', booking=booking, hotel=hotel, existing_review=existing_review)
        
        # Update existing review or create new one
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment if comment else None
            db.session.commit()
            flash('Your review has been updated!', 'success')
        else:
            # Create new review
            review = Review(
                user_id=current_user.id,
                hotel_id=hotel.id,
                booking_id=booking_id,
                rating=rating,
                comment=comment if comment else None
            )
            db.session.add(review)
            db.session.commit()
            flash('Thank you for your review!', 'success')
        
        return redirect(url_for('main.hotel_detail', hotel_id=hotel.id))
    
    return render_template('main/write_review.html', booking=booking, hotel=hotel, existing_review=existing_review)

@bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
        
    # Check if booking is already cancelled
    if booking.status == 'CANCELLED':
        flash('This booking has already been cancelled.', 'info')
        return redirect(url_for('main.my_stays'))
    
    points_to_refund = 0
    breakfasts_to_refund = 0
    
    # Refund points if booking was paid with points
    if booking.points_used > 0:
        points_to_refund = booking.points_used
        current_user.points += points_to_refund
        
        # Create points transaction record for refund
        refund_transaction = PointsTransaction(
            user_id=current_user.id,
            booking_id=booking.id,
            points=points_to_refund,
            transaction_type='REFUNDED',
            description=f'Refund for cancelled booking at {booking.room_type.hotel.name}'
        )
        db.session.add(refund_transaction)
    
    # Refund breakfast voucher if one was used
    if booking.breakfast_voucher_used:
        voucher = MilestoneReward.query.get(booking.breakfast_voucher_used)
        if voucher and voucher.breakfasts_used > 0:
            # Refund the breakfasts used (one breakfast per room)
            breakfasts_to_refund = booking.rooms_count
            voucher.breakfasts_used = max(0, voucher.breakfasts_used - breakfasts_to_refund)
    
    # Mark booking as cancelled
    booking.status = 'CANCELLED'
    db.session.commit()
    
    # Show appropriate flash message
    refund_parts = []
    if points_to_refund > 0:
        refund_parts.append(f'{points_to_refund:,} points')
    if breakfasts_to_refund > 0:
        refund_parts.append(f'{breakfasts_to_refund} breakfast voucher(s)')
    
    if refund_parts:
        flash(f'Booking cancelled. {", ".join(refund_parts)} have been refunded to your account.', 'success')
    else:
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
    """Navigate to hotel detail page for rebooking"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    
    hotel = booking.room_type.hotel
    return redirect(url_for('main.hotel_detail', hotel_id=hotel.id))
    
@bp.route('/account')
@login_required
def account():
    """Enhanced account page with tier info and statistics"""
    # Check and process tier expiry (this will handle retention and downgrades)
    retention_status = current_user.check_tier_retention_status()
    db.session.commit()  # Commit any changes from retention check
    
    # Award points for completed stays
    points_awarded, tier_upgraded = award_points_for_completed_stays(current_user)
    if points_awarded > 0:
        flash(f'You earned {points_awarded} points from completed stays!', 'success')
    if tier_upgraded:
        flash(f'🎉 Congratulations! You\'ve been upgraded to {current_user.membership_level} status!', 'success')
    
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
    
    # Bookings with points redeemed for Rewards Wallet tab
    redeemed_transactions = PointsTransaction.query.filter_by(
        user_id=current_user.id, 
        transaction_type='REDEEMED'
    ).order_by(PointsTransaction.created_at.desc()).all()
    
    # Bookings paid with points
    points_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        payment_method='points'
    ).order_by(Booking.created_at.desc()).all()
    
    # Bookings with breakfast vouchers
    breakfast_voucher_bookings = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.breakfast_voucher_used.isnot(None)
    ).order_by(Booking.created_at.desc()).all()
    
    # Milestone rewards
    milestone_rewards = MilestoneReward.query.filter_by(
        user_id=current_user.id
    ).order_by(MilestoneReward.created_at.desc()).all()
    
    # Calculate milestone progress for current year
    from datetime import datetime
    current_year = datetime.now().year
    year_start = datetime(current_year, 1, 1).date()
    year_bookings = [b for b in all_bookings if b.check_in >= year_start and b.status == 'CONFIRMED']
    year_nights = sum((b.check_out - b.check_in).days for b in year_bookings)
    
    # Milestone thresholds: 20, 30, 40, 50, 60, 70, 80, 90, 100
    milestone_thresholds = [20, 30, 40, 50, 60, 70, 80, 90, 100]
    next_milestone_year = None
    for threshold in milestone_thresholds:
        if year_nights < threshold:
            next_milestone_year = threshold
            break
    
    if next_milestone_year is None:
        nights_to_milestone_year = 0
        milestone_progress_percent = 100
    else:
        prev_milestone = 0
        for threshold in milestone_thresholds:
            if threshold < next_milestone_year:
                prev_milestone = threshold
        nights_to_milestone_year = next_milestone_year - year_nights
        range_size = next_milestone_year - prev_milestone
        progress_in_range = year_nights - prev_milestone
        milestone_progress_percent = min(100, int((progress_in_range / range_size) * 100))
    
    # Check for unclaimed milestone rewards
    unclaimed_milestones = []
    for threshold in milestone_thresholds:
        if year_nights >= threshold:
            # Check if user has already claimed this milestone
            existing_reward = MilestoneReward.query.filter_by(
                user_id=current_user.id,
                milestone_nights=threshold
            ).first()
            if not existing_reward:
                unclaimed_milestones.append(threshold)
    
    # Tier progress (points-based)
    points_to_next = current_user.points_to_next_tier()
    next_tier = current_user.next_tier_name()
    tier_benefits = current_user.get_tier_benefits()
    
    # Define multipliers for comparison table (ensures consistency)
    multipliers = {
        'Club Member': 1.0,
        'Silver Elite': 1.2,
        'Gold Elite': 1.5,
        'Diamond Elite': 2.0,
        'Platinum Elite': 2.5
    }
    
    # Calculate nights-based tier progress
    # Tier thresholds (consistent with models.py): 
    # 10 nights = Silver Elite, 20 nights = Gold Elite, 70 nights = Diamond Elite, 200 nights = Platinum Elite
    # Note: 40 nights is also Gold Elite but is a milestone, not a tier upgrade
    
    # Determine current tier based on nights (matching models.py logic)
    nights_current_tier = 'Club Member'
    if current_user.nights_stayed >= 200:
        nights_current_tier = 'Platinum Elite'
    elif current_user.nights_stayed >= 70:
        nights_current_tier = 'Diamond Elite'
    elif current_user.nights_stayed >= 20:  # 20 or 40 both = Gold Elite
        nights_current_tier = 'Gold Elite'
    elif current_user.nights_stayed >= 10:
        nights_current_tier = 'Silver Elite'
    
    # Calculate next tier threshold for nights (actual tier upgrades, not milestones)
    nights_next_tier = None
    nights_next_threshold = None
    if current_user.nights_stayed < 10:
        nights_next_tier = 'Silver Elite'
        nights_next_threshold = 10
        prev_milestone = 0
    elif current_user.nights_stayed < 20:
        nights_next_tier = 'Gold Elite'
        nights_next_threshold = 20
        prev_milestone = 10
    elif current_user.nights_stayed < 70:  # Skip 40 as it's not a tier upgrade, just a milestone
        nights_next_tier = 'Diamond Elite'
        nights_next_threshold = 70
        prev_milestone = 20  # Use 20 as previous milestone for progress calculation
    elif current_user.nights_stayed < 200:
        nights_next_tier = 'Platinum Elite'
        nights_next_threshold = 200
        prev_milestone = 70
    else:
        nights_next_tier = None
        nights_next_threshold = 200
        prev_milestone = 200
    
    if nights_next_tier is None:
        nights_to_next_milestone = 0
        nights_progress_percent = 100
    else:
        nights_to_next_milestone = nights_next_threshold - current_user.nights_stayed
        range_size = nights_next_threshold - prev_milestone
        progress_in_range = current_user.nights_stayed - prev_milestone
        nights_progress_percent = min(100, int((progress_in_range / range_size) * 100)) if range_size > 0 else 100
    
    # Calculate progress percentages and colors for progress bars
    # By Nights: 0-200 nights total
    nights_total_range = 200
    nights_stayed = current_user.nights_stayed
    nights_progress_pct = min(100, (nights_stayed / nights_total_range) * 100)
    
    # Calculate marker positions for nights tracker (equal proportion based on values)
    nights_marker_0_pct = (0 / nights_total_range) * 100
    nights_marker_10_pct = (10 / nights_total_range) * 100
    nights_marker_20_pct = (20 / nights_total_range) * 100
    nights_marker_70_pct = (70 / nights_total_range) * 100
    nights_marker_200_pct = (200 / nights_total_range) * 100
    
    # Determine current tier color for nights progress bar
    if nights_stayed >= 200:
        nights_bar_color = '#253639'  # Platinum
    elif nights_stayed >= 70:
        nights_bar_color = '#37283F'  # Diamond
    elif nights_stayed >= 20:
        nights_bar_color = '#A07A0D'  # Gold
    elif nights_stayed >= 10:
        nights_bar_color = '#606060'  # Silver
    else:
        nights_bar_color = '#d1d5db'  # Gray (Club Member)
    
    # By Points: 0-1M points total
    points_total_range = 1000000
    lifetime_points = current_user.lifetime_points
    points_total_progress_pct = min(100, (lifetime_points / points_total_range) * 100)
    
    # Calculate marker positions for points tracker (equal proportion based on values)
    points_marker_0_pct = (0 / points_total_range) * 100
    points_marker_50k_pct = (50000 / points_total_range) * 100
    points_marker_100k_pct = (100000 / points_total_range) * 100
    points_marker_500k_pct = (500000 / points_total_range) * 100
    points_marker_1m_pct = (1000000 / points_total_range) * 100
    
    # Determine current tier color for points progress bar
    if lifetime_points >= 1000000:
        points_bar_color = '#253639'  # Platinum
    elif lifetime_points >= 500000:
        points_bar_color = '#37283F'  # Diamond
    elif lifetime_points >= 100000:
        points_bar_color = '#A07A0D'  # Gold
    elif lifetime_points >= 50000:
        points_bar_color = '#606060'  # Silver
    else:
        points_bar_color = '#d1d5db'  # Gray (Club Member)
    
    # Calculate progress percentage for tier (points-based)
    tier_thresholds = {
        'Club Member': (0, 50000),
        'Silver Elite': (50000, 100000),
        'Gold Elite': (100000, 500000),
        'Diamond Elite': (500000, 1000000),
        'Platinum Elite': (1000000, 1000000)
    }
    current_threshold = tier_thresholds.get(current_user.membership_level, (0, 50000))
    if current_user.membership_level == 'Platinum Elite':
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
                         redeemed_transactions=redeemed_transactions,
                         points_bookings=points_bookings,
                         breakfast_voucher_bookings=breakfast_voucher_bookings,
                         milestone_rewards=milestone_rewards,
                         points_to_next=points_to_next,
                         next_tier=next_tier,
                         tier_benefits=tier_benefits,
                         progress_percent=progress_percent,
                         nights_to_next_milestone=nights_to_next_milestone,
                         nights_progress_percent=nights_progress_percent,
                         nights_next_tier=nights_next_tier or 'Platinum Elite',
                         nights_progress_pct=nights_progress_pct,
                         nights_bar_color=nights_bar_color,
                         nights_marker_0_pct=nights_marker_0_pct,
                         nights_marker_10_pct=nights_marker_10_pct,
                         nights_marker_20_pct=nights_marker_20_pct,
                         nights_marker_70_pct=nights_marker_70_pct,
                         nights_marker_200_pct=nights_marker_200_pct,
                         points_total_progress_pct=points_total_progress_pct,
                         points_bar_color=points_bar_color,
                         points_marker_0_pct=points_marker_0_pct,
                         points_marker_50k_pct=points_marker_50k_pct,
                         points_marker_100k_pct=points_marker_100k_pct,
                         points_marker_500k_pct=points_marker_500k_pct,
                         points_marker_1m_pct=points_marker_1m_pct,
                         multipliers=multipliers,
                         tier_retention=current_user.check_tier_retention_status(),
                         tier_requirements=current_user.get_tier_retention_requirements(),
                         year_nights=year_nights,
                         next_milestone_year=next_milestone_year or 100,
                         nights_to_milestone_year=nights_to_milestone_year,
                         milestone_progress_percent=milestone_progress_percent,
                         current_year=current_year,
                         unclaimed_milestones=unclaimed_milestones)

@bp.route('/milestone-rewards/<int:milestone_nights>', methods=['GET', 'POST'])
@login_required
def claim_milestone_reward(milestone_nights):
    """Display milestone reward selection page or process reward claim"""
    from ..models import MilestoneReward
    from datetime import datetime
    
    # Validate milestone threshold
    valid_milestones = [20, 30, 40, 50, 60, 70, 80, 90, 100]
    if milestone_nights not in valid_milestones:
        flash('Invalid milestone.', 'danger')
        return redirect(url_for('main.account'))
    
    # Check if user has reached this milestone
    current_year = datetime.now().year
    year_start = datetime(current_year, 1, 1).date()
    all_bookings = current_user.bookings
    year_bookings = [b for b in all_bookings if b.check_in >= year_start and b.status == 'CONFIRMED']
    year_nights = sum((b.check_out - b.check_in).days for b in year_bookings)
    
    if year_nights < milestone_nights:
        flash(f'You have not reached {milestone_nights} nights yet. You currently have {year_nights} nights this year.', 'warning')
        return redirect(url_for('main.account'))
    
    # Check if already claimed
    existing_reward = MilestoneReward.query.filter_by(
        user_id=current_user.id,
        milestone_nights=milestone_nights
    ).first()
    
    if existing_reward:
        flash('You have already claimed this milestone reward.', 'info')
        return redirect(url_for('main.account'))
    
    if request.method == 'POST':
        reward_type = request.form.get('reward_type')
        reward_value = int(request.form.get('reward_value', 0))
        
        if reward_type == 'points':
            # Award points
            current_user.points += reward_value
            transaction = PointsTransaction(
                user_id=current_user.id,
                points=reward_value,
                transaction_type='BONUS',
                description=f'Milestone reward: {milestone_nights} nights - {reward_value} bonus points'
            )
            db.session.add(transaction)
            flash(f'Congratulations! {reward_value:,} bonus points have been added to your account.', 'success')
        elif reward_type == 'breakfast':
            # Store breakfast reward (will be applied on next booking)
            flash(f'Congratulations! You have earned {reward_value} complimentary breakfasts. They will be available on your next booking.', 'success')
        
        # Create milestone reward record
        milestone_reward = MilestoneReward(
            user_id=current_user.id,
            milestone_nights=milestone_nights,
            reward_type=reward_type,
            reward_value=reward_value,
            claimed_at=datetime.utcnow()
        )
        db.session.add(milestone_reward)
        db.session.commit()
        
        return redirect(url_for('main.account'))
    
    # GET request - show selection page
    return render_template('main/milestone_rewards.html', milestone_nights=milestone_nights)

@bp.route('/account/milestone-progress')
@login_required
def milestone_progress():
    """Display milestone rewards progress page with rules and claimed rewards"""
    from datetime import datetime
    
    current_year = datetime.now().year
    year_start = datetime(current_year, 1, 1).date()
    all_bookings = current_user.bookings
    year_bookings = [b for b in all_bookings if b.check_in >= year_start and b.status == 'CONFIRMED']
    year_nights = sum((b.check_out - b.check_in).days for b in year_bookings)
    
    # Milestone thresholds: 20, 30, 40, 50, 60, 70, 80, 90, 100
    milestone_thresholds = [20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    # Get all milestone rewards for this user
    all_milestone_rewards = MilestoneReward.query.filter_by(
        user_id=current_user.id
    ).all()
    
    # Create a dictionary mapping milestone_nights to reward
    rewards_dict = {r.milestone_nights: r for r in all_milestone_rewards}
    
    # Build milestone progress list
    milestone_progress_list = []
    
    # Determine the current milestone (the one the user is working towards or needs to claim)
    # Priority: 1. First reached but unclaimed milestone. 2. First upcoming milestone.
    target_milestone_nights = None
    
    # First pass: check for unclaimed ones
    for threshold in milestone_thresholds:
        if year_nights >= threshold and threshold not in rewards_dict:
            target_milestone_nights = threshold
            break
            
    # If no unclaimed ones, find the first upcoming one
    if target_milestone_nights is None:
        for threshold in milestone_thresholds:
            if year_nights < threshold:
                target_milestone_nights = threshold
                break
    
    for threshold in milestone_thresholds:
        status = 'upcoming'
        if year_nights >= threshold:
            if threshold in rewards_dict:
                status = 'claimed'
            else:
                status = 'unclaimed'
        
        milestone_progress_list.append({
            'nights': threshold,
            'status': status,
            'reward': rewards_dict.get(threshold),
            'is_current': (threshold == target_milestone_nights)
        })
    
    return render_template('main/milestone_progress.html',
                         current_year=current_year,
                         year_nights=year_nights,
                         milestone_progress=milestone_progress_list)

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
