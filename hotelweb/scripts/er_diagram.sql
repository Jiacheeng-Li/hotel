-- ER Diagram SQL Export
-- Generated from SQLAlchemy models
-- Can be imported into:
--   - dbdiagram.io (DBML format recommended)
--   - MySQL Workbench
--   - pgAdmin
--   - DBeaver

-- Table: amenity
CREATE TABLE amenity (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE
);

-- Table: booking
CREATE TABLE booking (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  roomtype_id INTEGER NOT NULL,
  check_in DATE NOT NULL,
  check_out DATE NOT NULL,
  rooms_count INTEGER NOT NULL,
  status VARCHAR(20),
  created_at DATETIME,
  base_rate NUMERIC(10, 2),
  subtotal NUMERIC(10, 2),
  taxes NUMERIC(10, 2),
  fees NUMERIC(10, 2),
  total_cost NUMERIC(10, 2),
  points_earned INTEGER,
  points_used INTEGER,
  breakfast_included BOOLEAN,
  breakfast_price_per_room NUMERIC(10, 2),
  breakfast_voucher_used INTEGER,
  payment_method VARCHAR(20)
);

-- Table: brand
CREATE TABLE brand (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT,
  logo_color VARCHAR(20)
);

-- Table: contact_message
CREATE TABLE contact_message (
  id INTEGER PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(120) NOT NULL,
  subject VARCHAR(50) NOT NULL,
  message TEXT NOT NULL,
  created_at DATETIME,
  is_read BOOLEAN,
  user_id INTEGER
);

-- Table: favorite_hotel
CREATE TABLE favorite_hotel (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  hotel_id INTEGER NOT NULL,
  created_at DATETIME
);

-- Table: hotel
CREATE TABLE hotel (
  id INTEGER PRIMARY KEY,
  brand_id INTEGER,
  name VARCHAR(100) NOT NULL,
  city VARCHAR(50) NOT NULL,
  address VARCHAR(200) NOT NULL,
  description TEXT,
  image_url VARCHAR(200),
  stars INTEGER,
  latitude FLOAT,
  longitude FLOAT,
  breakfast_price NUMERIC(10, 2)
);

-- Table: milestone_reward
CREATE TABLE milestone_reward (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  milestone_nights INTEGER,
  reward_type VARCHAR(20) NOT NULL,
  reward_value INTEGER,
  breakfasts_used INTEGER,
  source VARCHAR(50),
  description VARCHAR(200),
  claimed_at DATETIME,
  created_at DATETIME
);

-- Table: payment_method
CREATE TABLE payment_method (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  card_type VARCHAR(20) NOT NULL,
  last4 VARCHAR(4) NOT NULL,
  expiry_month VARCHAR(2) NOT NULL,
  expiry_year VARCHAR(4) NOT NULL,
  cardholder_name VARCHAR(100) NOT NULL,
  is_default BOOLEAN,
  created_at DATETIME
);

-- Table: points_transaction
CREATE TABLE points_transaction (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  booking_id INTEGER,
  points INTEGER NOT NULL,
  transaction_type VARCHAR(20) NOT NULL,
  description VARCHAR(200),
  created_at DATETIME
);

-- Table: review
CREATE TABLE review (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  hotel_id INTEGER NOT NULL,
  booking_id INTEGER,
  rating INTEGER NOT NULL,
  comment TEXT,
  created_at DATETIME
);

-- Table: room_type
CREATE TABLE room_type (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER NOT NULL,
  name VARCHAR(100) NOT NULL,
  capacity INTEGER NOT NULL,
  price_per_night NUMERIC(10, 2) NOT NULL,
  inventory INTEGER NOT NULL,
  description TEXT,
  image_url VARCHAR(200)
);

-- Table: roomtype_amenity
CREATE TABLE roomtype_amenity (
  roomtype_id INTEGER PRIMARY KEY,
  amenity_id INTEGER PRIMARY KEY
);

-- Table: staff_hotel
CREATE TABLE staff_hotel (
  user_id INTEGER PRIMARY KEY,
  hotel_id INTEGER PRIMARY KEY
);

-- Table: user
CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(128),
  created_at DATETIME,
  role VARCHAR(20) NOT NULL,
  points INTEGER,
  lifetime_points INTEGER,
  nights_stayed INTEGER,
  membership_level VARCHAR(20),
  member_number VARCHAR(20) UNIQUE,
  tier_earned_date DATE,
  tier_expiry_date DATE,
  current_year_nights INTEGER,
  current_year_points INTEGER,
  phone VARCHAR(20),
  address VARCHAR(200),
  city VARCHAR(100),
  country VARCHAR(100),
  postal_code VARCHAR(20),
  birthday DATE
);

-- Table: user_event
CREATE TABLE user_event (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  event_year INTEGER NOT NULL,
  description VARCHAR(200),
  reward_type VARCHAR(20),
  reward_amount INTEGER,
  created_at DATETIME
);
