import sqlite3
import os
import time
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Database file path (centralized in base folder)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'curyent.db')


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_db():
    """Delete and recreate the database from scratch, clearing all data.
    If the file is locked, drop all tables instead of deleting the file."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            # File is locked — drop all tables to clear data in place
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table['name']}")
            conn.commit()
            conn.close()
    init_db()


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            title TEXT DEFAULT '',
            phone TEXT,
            location TEXT,
            profile_image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add title column to existing databases that don't have it
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN title TEXT DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create dj_equipment table for DJ-specific data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dj_equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pc_model TEXT,
            controller_model TEXT,
            mixer_model TEXT,
            speakers_model TEXT,
            speakers_quantity INTEGER,
            generator_model TEXT,
            generator_power REAL,
            projector_model TEXT,
            microphones_model TEXT,
            microphones_quantity INTEGER,
            instruments_name TEXT,
            instruments_quantity INTEGER,
            total_per_event REAL,
            national_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Migrate old 'daily_rate' column to 'total_per_event' in dj_equipment (for existing databases)
    try:
        cursor.execute("ALTER TABLE dj_equipment RENAME COLUMN daily_rate TO total_per_event")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already named total_per_event or table doesn't have daily_rate

    # Add verification image columns to dj_equipment (for existing databases)
    verification_image_columns = [
        "mixer_image TEXT",
        "speakers_image TEXT",
        "generator_image TEXT",
        "microphones_image TEXT",
        "instruments_image TEXT",
    ]
    for col_def in verification_image_columns:
        col_name = col_def.split()[0]
        try:
            cursor.execute(f"ALTER TABLE dj_equipment ADD COLUMN {col_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

    # Create otp_codes table for phone verification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at REAL NOT NULL,
            is_used INTEGER DEFAULT 0
        )
    ''')

    # Create event_venues table for venue data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            venue_name TEXT,
            venue_type TEXT,
            capacity INTEGER,
            amenities TEXT,
            event_description TEXT,
            daily_rate REAL,
            national_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create photographer_profiles table for photographer data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photographer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_name TEXT,
            specialization TEXT,
            experience INTEGER,
            camera_equipment TEXT,
            services TEXT,
            photographer_description TEXT,
            daily_rate REAL,
            national_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create tent_inventory table for tent rental data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tent_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_name TEXT,
            tent_types TEXT,
            tent_sizes TEXT,
            total_tents INTEGER,
            additional_equipment TEXT,
            delivery TEXT,
            delivery_areas TEXT,
            tent_description TEXT,
            daily_rate REAL,
            national_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create caterer_profiles table for catering data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caterer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_name TEXT,
            cuisine_type TEXT,
            per_person_rate REAL,
            max_guests INTEGER,
            min_guests INTEGER,
            menu_items TEXT,
            services TEXT,
            dietary_options TEXT,
            caterer_description TEXT,
            daily_rate REAL,
            national_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


def username_exists(username):
    """Check if a username already exists in the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def email_exists(email):
    """Check if an email already exists in the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def register_user(username, email, password, role, phone=None, location=None, profile_image=None, title=''):
    """Register a new user in the database. Password is hashed before storage."""
    # Hash the password before storing
    hashed_password = generate_password_hash(password)
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password, role, title, phone, location, profile_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (username, email, hashed_password, role, title, phone, location, profile_image)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_username(username):
    """Get a user by username."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    """Get a user by email."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user


# =========================
# OTP Functions
# =========================

def save_otp_code(phone, otp_code, expiry_seconds=300):
    """Save an OTP code to the database with expiration time."""
    conn = get_db()
    cursor = conn.cursor()
    expires_at = time.time() + expiry_seconds
    cursor.execute(
        'INSERT INTO otp_codes (phone, otp_code, expires_at) VALUES (?, ?, ?)',
        (phone, otp_code, expires_at)
    )
    conn.commit()
    conn.close()


def get_otp_code(phone):
    """
    Get the latest OTP code for a phone number.
    Returns None if no code exists or if the code has expired.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT otp_code, expires_at, is_used FROM otp_codes WHERE phone = ? ORDER BY id DESC LIMIT 1',
        (phone,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return None
    
    # Check if expired
    if time.time() > result['expires_at']:
        return None
    
    # Check if already used
    if result['is_used']:
        return None
    
    return result['otp_code']


def mark_otp_as_used(phone):
    """Mark the latest OTP code for a phone number as used."""
    conn = get_db()
    cursor = conn.cursor()
    # SQLite does not support ORDER BY + LIMIT in UPDATE, so use a subquery
    cursor.execute(
        'UPDATE otp_codes SET is_used = 1 WHERE id = (SELECT id FROM otp_codes WHERE phone = ? AND is_used = 0 ORDER BY id DESC LIMIT 1)',
        (phone,)
    )
    conn.commit()
    conn.close()


def verify_otp(phone, user_code):
    """
    Verify an OTP code for a phone number.
    Returns True if the code matches and is not expired.
    """
    stored_code = get_otp_code(phone)
    
    if stored_code is None:
        return False
    
    if stored_code.strip() == user_code.strip():
        mark_otp_as_used(phone)
        return True
    
    return False


def login_user(identifier, password):
    """
    Authenticate a user by email or username and password.
    Returns the user row if credentials are valid, None otherwise.
    Password is verified using secure hash comparison.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? OR username = ?', (identifier, identifier))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return user
    return None
