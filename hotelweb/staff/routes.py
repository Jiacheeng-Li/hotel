"""
Staff routes for hotel management
"""
from flask import render_template, request, url_for, redirect, flash, abort, jsonify
from flask_login import login_user, current_user
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from sqlalchemy import or_
from ..extensions import db
from ..models import User, Hotel, RoomType, Booking, Amenity
from ..utils.decorators import staff_required
from ..utils.security import validate_csrf_token, get_client_ip, check_login_attempts, record_login_attempt
from werkzeug.security import generate_password_hash
from . import bp

def verify_hotel_access(hotel_id):
    """Verify that the current staff user has access to this hotel"""
    if current_user.role == 'admin':
        return True  # Admins have access to all hotels
    hotel = Hotel.query.get_or_404(hotel_id)
    if hotel not in current_user.assigned_hotels.all():
        abort(403)
    return True

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Staff login page"""
    if current_user.is_authenticated:
        if current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        client_ip = get_client_ip()
        
        identifier = email if email else client_ip
        
        # Check login attempts
        allowed, remaining, lockout_until = check_login_attempts(identifier, max_attempts=5, lockout_duration=900)
        if not allowed:
            if lockout_until:
                now = datetime.now()
                if lockout_until > now:
                    minutes = int((lockout_until - now).total_seconds() / 60) + 1
                    flash(f'Too many failed login attempts. Please try again in {minutes} minute(s).', 'danger')
                else:
                    flash('Too many failed login attempts. Please try again later.', 'danger')
            else:
                flash('Too many failed login attempts. Please try again later.', 'danger')
            return render_template('staff/login.html')
        
        if not email or not password:
            record_login_attempt(identifier, False)
            flash('Email and password are required.', 'danger')
            return render_template('staff/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            password_valid = user.check_password(password)
        else:
            password_valid = False
        
        if user and password_valid:
            if user.role != 'staff':
                record_login_attempt(identifier, False)
                flash('Access denied. This is a staff-only area.', 'danger')
                return render_template('staff/login.html')
            
            record_login_attempt(identifier, True)
            login_user(user)
            flash('You have been logged in successfully.', 'success')
            return redirect(url_for('staff.dashboard'))
        else:
            record_login_attempt(identifier, False)
            flash('Invalid email or password. Please try again.', 'danger')
            if remaining and remaining < 5:
                flash(f'Warning: {remaining} attempt(s) remaining before account lockout.', 'warning')
    
    return render_template('staff/login.html')

@bp.route('/dashboard')
@staff_required
def dashboard():
    """Staff dashboard showing assigned hotels and recent bookings"""
    assigned_hotels = current_user.assigned_hotels.all()
    
    # Get recent bookings for assigned hotels
    hotel_ids = [h.id for h in assigned_hotels]
    recent_bookings = Booking.query.filter(
        Booking.roomtype_id.in_(
            db.session.query(RoomType.id).filter(RoomType.hotel_id.in_(hotel_ids))
        )
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get pending bookings (upcoming, not cancelled)
    today = date.today()
    pending_bookings = Booking.query.filter(
        Booking.roomtype_id.in_(
            db.session.query(RoomType.id).filter(RoomType.hotel_id.in_(hotel_ids))
        ),
        Booking.status == 'CONFIRMED',
        Booking.check_in >= today
    ).order_by(Booking.check_in.asc()).limit(10).all()
    
    return render_template('staff/dashboard.html',
                         hotels=assigned_hotels,
                         recent_bookings=recent_bookings,
                         pending_bookings=pending_bookings)

@bp.route('/hotels')
@staff_required
def hotels():
    """List all assigned hotels with search and pagination"""
    search = request.args.get('search', '').strip()
    city_filter = request.args.get('city', '').strip()
    brand_filter = request.args.get('brand', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get assigned hotel IDs
    assigned_hotel_ids = [h.id for h in current_user.assigned_hotels.all()]
    
    # Build query
    query = Hotel.query.filter(Hotel.id.in_(assigned_hotel_ids))
    
    if city_filter:
        query = query.filter(Hotel.city.ilike(f'%{city_filter}%'))
    
    if brand_filter:
        try:
            brand_id = int(brand_filter)
            query = query.filter(Hotel.brand_id == brand_id)
        except (ValueError, TypeError):
            pass
    
    if search:
        query = query.filter(
            or_(
                Hotel.name.ilike(f'%{search}%'),
                Hotel.city.ilike(f'%{search}%'),
                Hotel.address.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    hotels = pagination.items
    
    # Get unique cities for filter (from assigned hotels only)
    assigned_hotels = Hotel.query.filter(Hotel.id.in_(assigned_hotel_ids)).all()
    cities = sorted(list(set([h.city for h in assigned_hotels if h.city])))
    
    # Get brands for filter (from assigned hotels only)
    from ..models import Brand
    brand_ids = list(set([h.brand_id for h in assigned_hotels if h.brand_id]))
    brands = Brand.query.filter(Brand.id.in_(brand_ids)).order_by(Brand.name).all() if brand_ids else []
    
    return render_template('staff/hotels.html', 
                         hotels=hotels,
                         pagination=pagination,
                         search=search,
                         cities=cities,
                         brands=brands)

@bp.route('/hotels/<int:hotel_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit_hotel(hotel_id):
    """Edit hotel details, manage rooms, pricing, and breakfast price - all in one page"""
    verify_hotel_access(hotel_id)
    hotel = Hotel.query.get_or_404(hotel_id)
    
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or not validate_csrf_token(csrf_token):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('staff.edit_hotel', hotel_id=hotel_id))
        
        action = request.form.get('action', '')
        
        # Update hotel details
        if action == 'update_hotel':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            image_url = request.form.get('image_url', '').strip()
            breakfast_price = request.form.get('breakfast_price', type=float)
            
            if not name:
                flash('Hotel name is required.', 'danger')
            else:
                hotel.name = name
                hotel.description = description
                hotel.image_url = image_url
                
                # Update breakfast price
                if breakfast_price is not None:
                    try:
                        breakfast_price_decimal = Decimal(str(breakfast_price))
                        if breakfast_price_decimal < 0:
                            flash('Breakfast price cannot be negative.', 'danger')
                        else:
                            hotel.breakfast_price = breakfast_price_decimal
                    except (ValueError, InvalidOperation):
                        flash('Invalid breakfast price format.', 'danger')
                
                db.session.commit()
                flash('Hotel details updated successfully.', 'success')
        
        # Add new room
        elif action == 'add_room':
            name = request.form.get('room_name', '').strip()
            capacity = request.form.get('capacity', type=int)
            price_per_night = request.form.get('price_per_night', type=float)
            inventory = request.form.get('inventory', type=int)
            description = request.form.get('room_description', '').strip()
            image_url = request.form.get('room_image_url', '').strip()
            
            if not name:
                flash('Room name is required.', 'danger')
            elif not capacity or capacity < 1:
                flash('Capacity must be at least 1.', 'danger')
            elif not price_per_night or price_per_night <= 0:
                flash('Price per night must be greater than 0.', 'danger')
            elif not inventory or inventory < 1:
                flash('Inventory must be at least 1.', 'danger')
            else:
                room = RoomType(
                    hotel_id=hotel_id,
                    name=name,
                    capacity=capacity,
                    price_per_night=Decimal(str(price_per_night)),
                    inventory=inventory,
                    description=description,
                    image_url=image_url
                )
                
                # Add amenities
                amenity_ids = request.form.getlist('amenities')
                try:
                    amenity_ids = [int(aid) for aid in amenity_ids]
                    amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
                    room.amenities = amenities
                except (ValueError, TypeError):
                    pass
                
                db.session.add(room)
                db.session.commit()
                flash('Room added successfully.', 'success')
        
        # Update room details
        elif action == 'update_room':
            room_id = request.form.get('room_id', type=int)
            if not room_id:
                flash('Room ID is required.', 'danger')
            else:
                room = RoomType.query.get(room_id)
                if not room or room.hotel_id != hotel_id:
                    flash('Invalid room.', 'danger')
                else:
                    name = request.form.get('room_name', '').strip()
                    capacity = request.form.get('capacity', type=int)
                    price_per_night = request.form.get('price_per_night', type=float)
                    inventory = request.form.get('inventory', type=int)
                    description = request.form.get('room_description', '').strip()
                    image_url = request.form.get('room_image_url', '').strip()
                    
                    if not name:
                        flash('Room name is required.', 'danger')
                    elif not capacity or capacity < 1:
                        flash('Capacity must be at least 1.', 'danger')
                    elif not price_per_night or price_per_night <= 0:
                        flash('Price per night must be greater than 0.', 'danger')
                    elif not inventory or inventory < 1:
                        flash('Inventory must be at least 1.', 'danger')
                    else:
                        room.name = name
                        room.capacity = capacity
                        room.price_per_night = Decimal(str(price_per_night))
                        room.inventory = inventory
                        room.description = description
                        room.image_url = image_url
                        
                        # Update amenities
                        amenity_ids = request.form.getlist('amenities')
                        try:
                            amenity_ids = [int(aid) for aid in amenity_ids]
                            amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
                            room.amenities = amenities
                        except (ValueError, TypeError):
                            pass
                        
                        db.session.commit()
                        flash('Room updated successfully.', 'success')
        
        # Delete room
        elif action == 'delete_room':
            room_id = request.form.get('room_id', type=int)
            if not room_id:
                flash('Room ID is required.', 'danger')
            else:
                room = RoomType.query.get(room_id)
                if not room or room.hotel_id != hotel_id:
                    flash('Invalid room.', 'danger')
                else:
                    # Check if room has any bookings
                    has_bookings = Booking.query.filter_by(roomtype_id=room_id).first() is not None
                    if has_bookings:
                        flash('Cannot delete room type with existing bookings.', 'danger')
                    else:
                        db.session.delete(room)
                        db.session.commit()
                        flash('Room deleted successfully.', 'success')
        
        return redirect(url_for('staff.edit_hotel', hotel_id=hotel_id))
    
    # GET request - display hotel management page
    room_types = RoomType.query.filter_by(hotel_id=hotel_id).all()
    all_amenities = Amenity.query.all()
    
    return render_template('staff/edit_hotel.html', 
                         hotel=hotel, 
                         room_types=room_types,
                         all_amenities=all_amenities)

@bp.route('/rooms')
@staff_required
def rooms():
    """List all room types for assigned hotels with search and pagination"""
    search = request.args.get('search', '').strip()
    hotel_filter = request.args.get('hotel', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    assigned_hotels = current_user.assigned_hotels.all()
    hotel_ids = [h.id for h in assigned_hotels]
    
    query = RoomType.query.filter(RoomType.hotel_id.in_(hotel_ids))
    
    if hotel_filter:
        query = query.filter(RoomType.hotel_id == hotel_filter)
    
    if search:
        query = query.filter(
            or_(
                RoomType.name.ilike(f'%{search}%'),
                RoomType.description.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    room_types = pagination.items
    
    # Group by hotel for display
    rooms_by_hotel = {}
    for rt in room_types:
        if rt.hotel_id not in rooms_by_hotel:
            rooms_by_hotel[rt.hotel_id] = []
        rooms_by_hotel[rt.hotel_id].append(rt)
    
    return render_template('staff/rooms.html',
                         hotels=assigned_hotels,
                         rooms_by_hotel=rooms_by_hotel,
                         pagination=pagination,
                         search=search,
                         hotel_filter=hotel_filter)

@bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit_room(room_id):
    """Edit room type details"""
    room = RoomType.query.get_or_404(room_id)
    verify_hotel_access(room.hotel_id)
    
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or not validate_csrf_token(csrf_token):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('staff.edit_room', room_id=room_id))
        
        # Update room details
        name = request.form.get('name', '').strip()
        capacity = request.form.get('capacity', type=int)
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        if not name:
            flash('Room name is required.', 'danger')
            return render_template('staff/edit_room.html', room=room, all_amenities=Amenity.query.all())
        
        if not capacity or capacity < 1:
            flash('Capacity must be at least 1.', 'danger')
            return render_template('staff/edit_room.html', room=room, all_amenities=Amenity.query.all())
        
        room.name = name
        room.capacity = capacity
        room.description = description
        room.image_url = image_url
        
        # Update amenities
        amenity_ids = request.form.getlist('amenities')
        try:
            amenity_ids = [int(aid) for aid in amenity_ids]
            amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
            room.amenities = amenities
        except (ValueError, TypeError):
            pass
        
        db.session.commit()
        flash('Room details updated successfully.', 'success')
        return redirect(url_for('staff.rooms'))
    
    all_amenities = Amenity.query.all()
    return render_template('staff/edit_room.html', room=room, all_amenities=all_amenities)

@bp.route('/rooms/add', methods=['GET', 'POST'])
@staff_required
def add_room():
    """Add new room type"""
    assigned_hotels = current_user.assigned_hotels.all()
    
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or not validate_csrf_token(csrf_token):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('staff.add_room'))
        
        hotel_id = request.form.get('hotel_id', type=int)
        verify_hotel_access(hotel_id)
        
        name = request.form.get('name', '').strip()
        capacity = request.form.get('capacity', type=int)
        price_per_night = request.form.get('price_per_night', type=float)
        inventory = request.form.get('inventory', type=int)
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # Validation
        if not name:
            flash('Room name is required.', 'danger')
            return render_template('staff/add_room.html', hotels=assigned_hotels, all_amenities=Amenity.query.all())
        
        if not capacity or capacity < 1:
            flash('Capacity must be at least 1.', 'danger')
            return render_template('staff/add_room.html', hotels=assigned_hotels, all_amenities=Amenity.query.all())
        
        if not price_per_night or price_per_night <= 0:
            flash('Price per night must be greater than 0.', 'danger')
            return render_template('staff/add_room.html', hotels=assigned_hotels, all_amenities=Amenity.query.all())
        
        if not inventory or inventory < 1:
            flash('Inventory must be at least 1.', 'danger')
            return render_template('staff/add_room.html', hotels=assigned_hotels, all_amenities=Amenity.query.all())
        
        # Create room
        room = RoomType(
            hotel_id=hotel_id,
            name=name,
            capacity=capacity,
            price_per_night=Decimal(str(price_per_night)),
            inventory=inventory,
            description=description,
            image_url=image_url
        )
        
        # Add amenities
        amenity_ids = request.form.getlist('amenities')
        try:
            amenity_ids = [int(aid) for aid in amenity_ids]
            amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
            room.amenities = amenities
        except (ValueError, TypeError):
            pass
        
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully.', 'success')
        return redirect(url_for('staff.rooms'))
    
    all_amenities = Amenity.query.all()
    return render_template('staff/add_room.html', hotels=assigned_hotels, all_amenities=all_amenities)

@bp.route('/pricing')
@staff_required
def pricing():
    """Manage pricing and inventory for room types with search and pagination"""
    search = request.args.get('search', '').strip()
    hotel_filter = request.args.get('hotel', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    assigned_hotels = current_user.assigned_hotels.all()
    hotel_ids = [h.id for h in assigned_hotels]
    
    query = RoomType.query.filter(RoomType.hotel_id.in_(hotel_ids))
    
    if hotel_filter:
        query = query.filter(RoomType.hotel_id == hotel_filter)
    
    if search:
        query = query.filter(
            or_(
                RoomType.name.ilike(f'%{search}%'),
                RoomType.description.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    room_types = pagination.items
    
    return render_template('staff/pricing.html', 
                         room_types=room_types,
                         hotels=assigned_hotels,
                         pagination=pagination,
                         search=search,
                         hotel_filter=hotel_filter)

@bp.route('/pricing/update', methods=['POST'])
@staff_required
def update_pricing():
    """Update pricing and inventory via AJAX"""
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Invalid request format.'}), 400
    
    data = request.get_json()
    room_id = data.get('room_id')
    price = data.get('price')
    inventory = data.get('inventory')
    
    if not room_id:
        return jsonify({'success': False, 'message': 'Room ID is required.'}), 400
    
    room = RoomType.query.get_or_404(room_id)
    verify_hotel_access(room.hotel_id)
    
    # Validate and update price
    if price is not None:
        try:
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                return jsonify({'success': False, 'message': 'Price must be greater than 0.'}), 400
            room.price_per_night = price_decimal
        except (ValueError, InvalidOperation):
            return jsonify({'success': False, 'message': 'Invalid price format.'}), 400
    
    # Validate and update inventory
    if inventory is not None:
        try:
            inventory_int = int(inventory)
            if inventory_int < 1:
                return jsonify({'success': False, 'message': 'Inventory must be at least 1.'}), 400
            room.inventory = inventory_int
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid inventory format.'}), 400
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Pricing updated successfully.'})

@bp.route('/hotels/<int:hotel_id>/breakfast-price', methods=['POST'])
@staff_required
def update_breakfast_price(hotel_id):
    """Update breakfast price via AJAX"""
    verify_hotel_access(hotel_id)
    hotel = Hotel.query.get_or_404(hotel_id)
    
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Invalid request format.'}), 400
    
    data = request.get_json()
    breakfast_price = data.get('breakfast_price')
    
    if breakfast_price is None:
        return jsonify({'success': False, 'message': 'Breakfast price is required.'}), 400
    
    try:
        breakfast_price_decimal = Decimal(str(breakfast_price))
        if breakfast_price_decimal < 0:
            return jsonify({'success': False, 'message': 'Breakfast price cannot be negative.'}), 400
        hotel.breakfast_price = breakfast_price_decimal
        db.session.commit()
        return jsonify({'success': True, 'message': 'Breakfast price updated successfully.'})
    except (ValueError, InvalidOperation):
        return jsonify({'success': False, 'message': 'Invalid breakfast price format.'}), 400

@bp.route('/bookings')
@staff_required
def bookings():
    """View bookings for assigned hotels with search and pagination"""
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    assigned_hotels = current_user.assigned_hotels.all()
    hotel_ids = [h.id for h in assigned_hotels]
    
    # Get all bookings for assigned hotels
    query = Booking.query.filter(
        Booking.roomtype_id.in_(
            db.session.query(RoomType.id).filter(RoomType.hotel_id.in_(hotel_ids))
        )
    )
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    if search:
        query = query.join(User).filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(Booking.check_in.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    bookings = pagination.items
    
    return render_template('staff/bookings.html', 
                         bookings=bookings,
                         pagination=pagination,
                         search=search,
                         status_filter=status_filter)

@bp.route('/bookings/<int:booking_id>/confirm', methods=['POST'])
@staff_required
def confirm_booking(booking_id):
    """Confirm a booking (mark as confirmed)"""
    booking = Booking.query.get_or_404(booking_id)
    verify_hotel_access(booking.room_type.hotel_id)
    
    if booking.status == 'CONFIRMED':
        return jsonify({'success': False, 'message': 'Booking is already confirmed.'}), 400
    
    booking.status = 'CONFIRMED'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Booking confirmed successfully.'})

@bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@staff_required
def cancel_booking(booking_id):
    """Cancel a booking (mark as cancelled)"""
    booking = Booking.query.get_or_404(booking_id)
    verify_hotel_access(booking.room_type.hotel_id)
    
    if booking.status == 'CANCELLED':
        return jsonify({'success': False, 'message': 'Booking is already cancelled.'}), 400
    
    booking.status = 'CANCELLED'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Booking cancelled successfully.'})

