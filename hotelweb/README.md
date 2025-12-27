# Hotel Group Platform

A premium hotel booking web application built with Flask, featuring availability search, amenity filtering, and a responsive design.

## Features

- **User Authentication**: Register, Login, Logout with secure password hashing.
- **Search & Availability**: Real-time room availability check based on dates and inventory.
- **Filtering**: Filter by city, guests, date range, and amenities.
- **Booking Management**: Book rooms and cancel existing bookings.
- **Premium UI**: Responsive design with custom CSS and accessible components.
- **Database**: SQLite for development, configured for easy switch to MySQL (PythonAnywhere).

## Prerequisites

- Python 3.8+
- `pip`

## Installation

1.  Clone the repository and navigate to the project folder:
    ```bash
    cd hotelweb
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Initialize Database & Seed Data:
    This script will drop existing tables and repopulate with fresh test data (Cities, Hotels, Rooms, Amenities).
    ```bash
    python scripts/seed_data.py
    ```

## Usage

1.  Run the application:
    ```bash
    # The easiest way:
    python run.py
    
    # Or using Flask CLI:
    export FLASK_APP=hotelweb
    flask run
    ```

2.  Open your browser at `http://127.0.0.1:5000`.

3.  **Test Account**:
    - **Email**: `test@example.com`
    - **Password**: `password`
    - *(Or register a new account)*

## Deployment (PythonAnywhere)

1.  Upload the code to PythonAnywhere.
2.  Set up a Virtualenv and install requirements.
3.  Configure the `DATABASE_URL` environment variable if using MySQL (otherwise it defaults to SQLite in `instance/hotel.db`).
4.  Set `SECRET_KEY` environment variable.
5.  Configure WSGI file to point to `create_app()`.
6.  Set Static Files mapping: URL `/static/` -> Directory `/home/yourusername/hotelweb/static/`.

## Project Structure

```text
hotelweb/
├── app.py              # Application Factory
├── config.py           # Configuration
├── extensions.py       # SQLAlchemy, LoginManager
├── models.py           # Database Models
├── auth/               # Authentication Blueprint
├── main/               # Core Logic Blueprint
│   ├── routes.py       # Views (Search, Booking)
│   └── services.py     # Search Algorithms
├── scripts/
│   └── seed_data.py    # Database Seeding Script
├── static/             # CSS/JS Assets
└── templates/          # Jinja2 Templates
```
