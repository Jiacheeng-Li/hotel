# Lumina Hotel Group Platform

A comprehensive hotel booking and management web application built with Flask, featuring multi-role access control, real-time availability search, loyalty program, and administrative tools.

## 🌟 Features

### Customer Features
- **User Authentication**: Secure registration, login, and logout with password hashing
- **Advanced Search**: Real-time room availability check based on dates, guests, and inventory
- **Smart Filtering**: Filter by city, brand, guests, date range, and amenities
- **Booking Management**: Book rooms, cancel bookings, and view booking history
- **Favorites System**: Save favorite hotels with AJAX-powered toggle
- **Loyalty Program**: 
  - Points earning and redemption system
  - Membership tiers (Club Member, Silver Elite, Gold Elite, Diamond Elite, Platinum Elite)
  - Milestone rewards based on nights stayed
  - Breakfast vouchers and special event bonuses (birthday, New Year)
- **Reviews & Ratings**: Write and view hotel reviews with booking verification
- **Payment Options**: 
  - Credit/debit card payment
  - Pay at hotel
  - Points redemption (100 points = $1.00)
  - Breakfast voucher usage
- **Account Management**: 
  - Profile settings with AJAX updates
  - Payment method management
  - Booking history and statistics
  - Tier progress tracking

### Staff Features (Hotel Management)
- **Hotel Management**: View and edit assigned hotels only
- **Room Management**: Add, edit, and delete room types
- **Pricing & Inventory**: Set room prices and manage inventory
- **Booking Management**: View, confirm, and cancel bookings for assigned hotels
- **Search & Filter**: Search hotels by name, city, and brand

### Admin Features (Platform Management)
- **User Management**: View all users, create staff/admin accounts, assign hotels to staff
- **Hotel Management**: View all hotels, manage hotel details, delete reviews
- **Contact Messages**: View and manage customer inquiries from "Contact Us" form
- **Points Management**: Grant points to users
- **Search & Filter**: Advanced search and filtering for all entities

## 🛠️ Technology Stack

- **Backend**: Flask 2.0+
- **Database**: SQLite (development), MySQL compatible (production)
- **ORM**: SQLAlchemy 2.0+ via Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **Security**: 
  - CSRF protection
  - Login attempt limiting
  - Input validation and sanitization
  - Password hashing with Werkzeug
- **Frontend**: 
  - Bootstrap 5 for responsive UI
  - Vanilla JavaScript (all externalized)
  - Custom CSS for branding
- **Email Validation**: email-validator

## 📋 Prerequisites

- Python 3.8+
- `pip` package manager

## 🚀 Installation

1. **Clone the repository and navigate to the project folder:**
   ```bash
   cd hotel
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database & Seed Data:**
   This script will drop existing tables and repopulate with fresh test data (Cities, Hotels, Rooms, Amenities, Brands).
   ```bash
   python hotelweb/scripts/seed_data.py
   ```

   After running the seed script, the following test accounts will be created:

   **Customer Test Accounts** (password: `testuser123`):
   - **Club Member**: club01@test.com, club02@test.com
   - **Silver Elite**: silver01@test.com, silver02@test.com
   - **Gold Elite**: gold01@test.com, gold02@test.com
   - **Diamond Elite**: diamond01@test.com, diamond02@test.com
   - **Platinum Elite**: platinum01@test.com, platinum02@test.com

   **Management Accounts**:
   - **Admin**: admin@lumina.com / admin123
   - **Staff**: staff@lumina.com / staff123

5. **Create Admin Account (Optional):**
   ```bash
   python hotelweb/scripts/tools/create_admin.py
   ```

6. **Create Staff Account (Optional):**
   ```bash
   python hotelweb/scripts/tools/create_staff.py
   ```

## 💻 Usage

### Running the Application

1. **Start the development server:**
   ```bash
   python run.py
   ```
   
   Or using Flask CLI:
   ```bash
   export FLASK_APP=hotelweb
   flask run
   ```

2. **Open your browser at `http://127.0.0.1:5000`**

### Access Points

- **Customer Portal**: `http://127.0.0.1:5000/`
- **Staff Portal**: `http://127.0.0.1:5000/staff/login`
- **Admin Portal**: `http://127.0.0.1:5000/admin/login`

### Test Accounts

After running `seed_data.py`, you can use the pre-created test accounts (see Installation section above) or register a new customer account.

## 📁 Project Structure

```
hotel/
├── hotelweb/                    # Main application package
│   ├── app.py                   # Flask application factory
│   ├── config.py                # Configuration (env vars, database)
│   ├── extensions.py            # Flask extensions (db, login_manager)
│   ├── models.py                # Database models (User, Hotel, Booking, etc.)
│   ├── auth/                    # Authentication blueprint
│   │   └── routes.py            # Login, register, logout
│   ├── main/                    # Customer frontend blueprint
│   │   ├── routes.py            # Main routes (search, booking, account)
│   │   ├── payment_routes.py    # Payment processing
│   │   └── services.py          # Business logic (search algorithms)
│   ├── admin/                   # Admin portal blueprint
│   │   └── routes.py            # Admin routes (users, hotels, messages)
│   ├── staff/                   # Staff portal blueprint
│   │   └── routes.py            # Staff routes (hotels, bookings)
│   ├── utils/                   # Utility modules
│   │   ├── decorators.py       # Role-based access decorators
│   │   └── security.py         # Security utilities (CSRF, validation)
│   ├── static/                  # Static assets
│   │   ├── css/                 # Stylesheets (main, admin, staff)
│   │   ├── js/                  # JavaScript files (all externalized)
│   │   └── img/                 # Images (logos, hotel photos)
│   │       ├── hotels/          # Hotel images (sourced from Unsplash/Pexels)
│   │       ├── rooms/           # Room type images (sourced from Unsplash/Pexels)
│   │       └── cities/          # City background images (sourced from Unsplash/Pexels)
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   ├── auth/                # Authentication templates
│   │   ├── main/                # Customer frontend templates
│   │   ├── admin/               # Admin portal templates
│   │   └── staff/               # Staff portal templates
│   └── scripts/                 # Utility scripts
│       ├── seed_data.py         # Database seeding
│       └── tools/                # Helper scripts (create accounts, etc.)
├── migrations/                  # Database migration scripts (archived)
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## 🔒 Security Features

- **CSRF Protection**: All forms protected with CSRF tokens
- **Password Security**: 
  - Werkzeug password hashing
  - Password complexity requirements (8-16 chars, alphanumeric)
- **Login Security**: 
  - Login attempt limiting
  - User enumeration prevention
- **Input Validation**: 
  - Client-side and server-side validation
  - XSS and SQL injection prevention
  - Sanitization of user inputs
- **Role-Based Access Control**: 
  - `@login_required` decorator
  - `@staff_required` decorator
  - `@admin_required` decorator
  - Ownership validation for staff


## 📝 Key Features Details

### Membership Tiers
- **Club Member**: 0-49,999 lifetime points
- **Silver Elite**: 50,000-99,999 lifetime points
- **Gold Elite**: 100,000-499,999 lifetime points
- **Diamond Elite**: 500,000-999,999 lifetime points
- **Platinum Elite**: 1,000,000+ lifetime points

### Milestone Rewards
- Rewards based on nights stayed in the current year
- Breakfast vouchers and points bonuses
- Automatic milestone tracking

### Special Events
- **Birthday Bonus**: 1,000 points on user's birthday
- **New Year Gift**: Breakfast voucher on January 1st

## 🧪 Development Notes

- All JavaScript code is externalized to separate `.js` files in `static/js/`
- All CSS is in separate files in `static/css/`
- Database migrations are archived in `migrations/` directory
- The application uses Flask's application factory pattern for easy testing and deployment

## 📸 Image Credits

All photos used in this application (hotels, rooms, cities, backgrounds) are sourced from:
- **Unsplash** (https://unsplash.com)
- **Pexels** (https://www.pexels.com)

Logo is generated by **nanobanana**.

All images and logo are **free for commercial use**.

These images have been downloaded and stored locally in the `static/img/` directory for use in the application.

## 📄 License

This project is for educational/demonstration purposes.

## ✍️ Author

Jiacheng Li
