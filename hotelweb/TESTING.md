# Testing & Verification Report

## 1. Functional Testing Checklist

| Feature | Scenario | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Authentication** | Register new user | ✅ Pass | Validated duplicate email/username checks. |
| | Login with valid/invalid credentials | ✅ Pass | "Login Unsuccessful" flash message works. |
| | Logout | ✅ Pass | Redirects to home, session cleared. |
| **Search** | Empty search | ✅ Pass | Prompts for required fields. |
| | Date Logic (Check-out <= Check-in) | ✅ Pass | Blocked with warning message. |
| | **Availability (Core)** | Overlap Detection | ✅ Pass | Fully booked rooms do not appear in results. |
| | Inventory Check | ✅ Pass | Rooms appear until inventory reaches 0. |
| **Filters** | Amenity Filtering | ✅ Pass | Only shows rooms containing ALL selected amenities. |
| | Capacity Check | ✅ Pass | Rooms with capacity < guests are hidden. |
| **Booking** | Create Booking | ✅ Pass | Inventory deducted (logically checked via search). |
| | Cancel Booking | ✅ Pass | Status changes to CANCELLED. |
| **Permissions** | Cancel other's booking | ✅ Pass | Returns 403 Forbidden. |
| | Access My Bookings when logged out | ✅ Pass | Redirects to Login. |

## 2. Accessibility (WCAG Compliance)

- **Semantic HTML**: Used `<nav>`, `<main>` (via container), `<header>` (navbar), `<footer>`.
- **Forms**: All inputs have associated `<label>` elements.
- **Keyboard Navigation**:
    - Focus visible on all inputs and buttons (default browser outline preserved/enhanced).
    - Tab order matches visual order.
- **Images**: All `<img>` tags have `alt` attributes (dynamic from DB or placeholder text).
- **Contrast**:
    - Primary text `#1e293b` on `#f8fafc` background (High Contrast).
    - Buttons use Bootstrap primary/dark colors compliant with WCAG AA.

## 3. Responsive Design

- **Mobile (< 576px)**:
    - Navbar collapses into hamburger menu.
    - Card grid becomes single column.
    - Padding adjusts for smaller screens.
- **Tablet (768px)**:
    - Sidebar filter remains accessible or stacks depending on width.
- **Desktop**:
    - Full 12-column grid layout.
    - Sticky sidebar for filters on Search page.

## 4. Manual Verification Steps

To verify the core "Availability Algorithm":

1.  **Seed Data**: Run `python scripts/seed_data.py` to reset data.
2.  **Login**: Use `test@example.com` / `password`.
3.  **Search**: Search for "New York", Date T to T+2, Guests 2.
4.  **Note Inventory**: Pick a room (e.g., "Standard Room") with Inventory X.
5.  **Book**: Book X times (or book 1 time with `rooms_needed=X`).
6.  **Re-Search**: Search same dates again.
7.  **Result**: The room type should **NOT** appear in results (or show distinct availability if partially booked).
8.  **Cancel**: Go to My Bookings, Cancel one.
9.  **Re-Search**: The room should satisfy search again.

## 5. Security Checks

- **SQL Injection**: Prevented by using SQLAlchemy ORM.
- **XSS**: Prevented by Jinja2 auto-escaping.
- **CSRF**: (Basic Flask-WTF or manual checks recommended for prod, currently relying on basic form handling sufficient for MVP).
- **Password Storage**: Uses `werkzeug.security` PBKDF2 SHA256 hashing.
