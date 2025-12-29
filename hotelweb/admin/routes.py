"""
Admin routes for platform management
"""
from flask import render_template, request, url_for, redirect, flash, abort, jsonify
from flask_login import login_user, current_user
from datetime import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy import or_
from ..extensions import db
from ..models import User, Hotel, RoomType, Booking, Review, PointsTransaction, ContactMessage, Amenity
from ..utils.decorators import admin_required
from ..utils.security import validate_csrf_token, get_client_ip, check_login_attempts, record_login_attempt
from werkzeug.security import generate_password_hash
from . import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
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
            return render_template('admin/login.html')
        
        if not email or not password:
            record_login_attempt(identifier, False)
            flash('Email and password are required.', 'danger')
            return render_template('admin/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            password_valid = user.check_password(password)
        else:
            password_valid = False
        
        if user and password_valid:
            if user.role != 'admin':
                record_login_attempt(identifier, False)
                flash('Access denied. This is an admin-only area.', 'danger')
                return render_template('admin/login.html')
            
            record_login_attempt(identifier, True)
            login_user(user)
            flash('You have been logged in successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            record_login_attempt(identifier, False)
            flash('Invalid email or password. Please try again.', 'danger')
            if remaining and remaining < 5:
                flash(f'Warning: {remaining} attempt(s) remaining before account lockout.', 'warning')
    
    return render_template('admin/login.html')

@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with platform statistics"""
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_hotels = Hotel.query.count()
    total_bookings = Booking.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_customers=total_customers,
                         total_staff=total_staff,
                         total_hotels=total_hotels,
                         total_bookings=total_bookings,
                         recent_users=recent_users,
                         recent_bookings=recent_bookings)

@bp.route('/users')
@admin_required
def users():
    """View all users with roles, search and pagination"""
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = User.query
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(User.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template('admin/users.html', 
                         users=users,
                         pagination=pagination,
                         search=search,
                         role_filter=role_filter)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user details and role"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or not validate_csrf_token(csrf_token):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Update user details
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', '').strip()
        
        if not username:
            flash('Username is required.', 'danger')
            return render_template('admin/edit_user.html', user=user, all_hotels=Hotel.query.all())
        
        if not email:
            flash('Email is required.', 'danger')
            return render_template('admin/edit_user.html', user=user, all_hotels=Hotel.query.all())
        
        if role not in ['customer', 'staff', 'admin']:
            flash('Invalid role.', 'danger')
            return render_template('admin/edit_user.html', user=user, all_hotels=Hotel.query.all())
        
        # Check for duplicate username/email
        existing_username = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_username:
            flash('Username already taken.', 'danger')
            return render_template('admin/edit_user.html', user=user, all_hotels=Hotel.query.all())
        
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('Email already taken.', 'danger')
            return render_template('admin/edit_user.html', user=user, all_hotels=Hotel.query.all())
        
        user.username = username
        user.email = email
        user.role = role
        
        # Update password if provided
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            user.set_password(new_password)
        
        # Update assigned hotels for staff
        if role == 'staff':
            hotel_ids = request.form.getlist('hotels')
            try:
                hotel_ids = [int(hid) for hid in hotel_ids]
                hotels = Hotel.query.filter(Hotel.id.in_(hotel_ids)).all()
                user.assigned_hotels = hotels
            except (ValueError, TypeError):
                pass
        else:
            # Clear assigned hotels for non-staff
            user.assigned_hotels = []
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    all_hotels = Hotel.query.all()
    return render_template('admin/edit_user.html', user=user, all_hotels=all_hotels)

@bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create new user (staff or admin)"""
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or not validate_csrf_token(csrf_token):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('admin.create_user'))
        
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip()
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('admin/create_user.html', all_hotels=Hotel.query.all())
        
        if role not in ['staff', 'admin']:
            flash('Invalid role. Only staff and admin can be created here.', 'danger')
            return render_template('admin/create_user.html', all_hotels=Hotel.query.all())
        
        # Check for existing user
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/create_user.html', all_hotels=Hotel.query.all())
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/create_user.html', all_hotels=Hotel.query.all())
        
        # Create user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        # Assign hotels for staff
        if role == 'staff':
            hotel_ids = request.form.getlist('hotels')
            try:
                hotel_ids = [int(hid) for hid in hotel_ids]
                hotels = Hotel.query.filter(Hotel.id.in_(hotel_ids)).all()
                user.assigned_hotels = hotels
            except (ValueError, TypeError):
                pass
        
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    all_hotels = Hotel.query.all()
    return render_template('admin/create_user.html', all_hotels=all_hotels)

@bp.route('/users/<int:user_id>/grant-points', methods=['POST'])
@admin_required
def grant_points(user_id):
    """Grant points to a user via AJAX"""
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Invalid request format.'}), 400
    
    data = request.get_json()
    points = data.get('points')
    description = data.get('description', 'Admin grant')
    
    if not points:
        return jsonify({'success': False, 'message': 'Points amount is required.'}), 400
    
    try:
        points_int = int(points)
        if points_int <= 0:
            return jsonify({'success': False, 'message': 'Points must be greater than 0.'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid points format.'}), 400
    
    user = User.query.get_or_404(user_id)
    user.points += points_int
    user.lifetime_points += points_int
    
    # Create transaction record
    transaction = PointsTransaction(
        user_id=user.id,
        points=points_int,
        transaction_type='BONUS',
        description=description
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'{points_int:,} points granted successfully.', 'new_balance': user.points})

@bp.route('/hotels')
@admin_required
def hotels():
    """View all hotels with search and pagination"""
    search = request.args.get('search', '').strip()
    city_filter = request.args.get('city', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = Hotel.query
    
    if city_filter:
        query = query.filter(Hotel.city.ilike(f'%{city_filter}%'))
    
    brand_filter = request.args.get('brand', '').strip()
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
    
    query = query.order_by(Hotel.name)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    hotels = pagination.items
    
    # Get unique cities for filter
    all_cities = db.session.query(Hotel.city).distinct().order_by(Hotel.city).all()
    cities = [c[0] for c in all_cities]
    
    # Get all brands for filter
    from ..models import Brand
    brands = Brand.query.order_by(Brand.name).all()
    
    return render_template('admin/hotels.html', 
                         hotels=hotels,
                         pagination=pagination,
                         search=search,
                         city_filter=city_filter,
                         cities=cities,
                         brands=brands)

@bp.route('/hotels/<int:hotel_id>/reviews')
@admin_required
def hotel_reviews(hotel_id):
    """View and manage reviews for a hotel with search and pagination"""
    search = request.args.get('search', '').strip()
    rating_filter = request.args.get('rating', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    hotel = Hotel.query.get_or_404(hotel_id)
    
    query = Review.query.filter_by(hotel_id=hotel_id)
    
    if rating_filter:
        query = query.filter(Review.rating == rating_filter)
    
    if search:
        query = query.join(User).filter(
            or_(
                User.username.ilike(f'%{search}%'),
                Review.comment.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(Review.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    reviews = pagination.items
    
    return render_template('admin/hotel_reviews.html', 
                         hotel=hotel, 
                         reviews=reviews,
                         pagination=pagination,
                         search=search,
                         rating_filter=rating_filter)

@bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@admin_required
def delete_review(review_id):
    """Delete a review via AJAX"""
    review = Review.query.get_or_404(review_id)
    hotel_id = review.hotel_id
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Review deleted successfully.'})

@bp.route('/hotels/<int:hotel_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_hotel(hotel_id):
    """Edit hotel details, manage rooms, pricing, and breakfast price - all in one page (Admin version)"""
    hotel = Hotel.query.get_or_404(hotel_id)
    
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or not validate_csrf_token(csrf_token):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('admin.edit_hotel', hotel_id=hotel_id))
        
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
        
        return redirect(url_for('admin.edit_hotel', hotel_id=hotel_id))
    
    # GET request - display hotel management page
    room_types = RoomType.query.filter_by(hotel_id=hotel_id).all()
    all_amenities = Amenity.query.all()
    
    return render_template('admin/edit_hotel.html', 
                         hotel=hotel, 
                         room_types=room_types,
                         all_amenities=all_amenities)

@bp.route('/messages')
@admin_required
def messages():
    """View all contact messages with search and pagination"""
    search = request.args.get('search', '').strip()
    subject_filter = request.args.get('subject', '').strip()
    read_filter = request.args.get('read', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = ContactMessage.query
    
    if subject_filter:
        query = query.filter(ContactMessage.subject == subject_filter)
    
    if read_filter == 'read':
        query = query.filter(ContactMessage.is_read == True)
    elif read_filter == 'unread':
        query = query.filter(ContactMessage.is_read == False)
    
    if search:
        query = query.filter(
            or_(
                ContactMessage.name.ilike(f'%{search}%'),
                ContactMessage.email.ilike(f'%{search}%'),
                ContactMessage.message.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(ContactMessage.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    messages = pagination.items
    
    return render_template('admin/messages.html', 
                         messages=messages,
                         pagination=pagination,
                         search=search,
                         subject_filter=subject_filter,
                         read_filter=read_filter)

@bp.route('/messages/<int:message_id>/read', methods=['POST'])
@admin_required
def mark_message_read(message_id):
    """Mark a message as read via AJAX"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message marked as read.'})

@bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@admin_required
def delete_message(message_id):
    """Delete a message via AJAX"""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message deleted successfully.'})

