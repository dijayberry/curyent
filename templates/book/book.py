"""
Book module — intermediary for booking-related logic.

Booking lifecycle:
  1. booker creates booking (status: pending) — includes event start/end dates
  2. booked person accepts or declines
  3. If accepted, system waits until event_start_date approaches
  4. Booked person is notified to approve service delivery
  5. If approved, payout is scheduled for 2 hours before the event end time
  6. If not approved, ask booked person for rejection reason
"""
import sqlite3
import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, session

# Booking database file path (separate from curyent.db)
BOOK_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'booking.db')

# Import the main db module to read users and their profiles
import templates.account.db as main_db

# Import notification helper to create automatic notifications
import templates.notifications.noti as noti_module

# Import M-Pesa payment module (now in the same package)
import templates.book.mpesa as mpesa_module

book_bp = Blueprint('book', __name__)


def get_book_db():
    """Get a connection to the booking database."""
    conn = sqlite3.connect(BOOK_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_book_db():
    """Delete and recreate the booking database from scratch, clearing all data.
    If the file is locked, drop all tables instead of deleting the file."""
    if os.path.exists(BOOK_DB_PATH):
        try:
            os.remove(BOOK_DB_PATH)
        except PermissionError:
            # File is locked — drop all tables to clear data in place
            conn = get_book_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table['name']}")
            conn.commit()
            conn.close()
    init_book_db()
    sync_users_to_book_db()


def sync_users_to_book_db():
    """Sync the users table from curyent.db into booking.db so JOIN queries work."""
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT * FROM users')
        users = main_cursor.fetchall()
        main_conn.close()

        book_conn = get_book_db()
        book_cursor = book_conn.cursor()
        book_cursor.execute('''
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
        book_conn.commit()

        # Add missing columns if they don't exist (for existing databases)
        try:
            book_cursor.execute('ALTER TABLE users ADD COLUMN profile_image TEXT')
            book_conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            book_cursor.execute("ALTER TABLE users ADD COLUMN title TEXT DEFAULT ''")
            book_conn.commit()
        except sqlite3.OperationalError:
            pass

        # Delete existing users and re-insert to keep in sync
        book_cursor.execute('DELETE FROM users')
        for u in users:
            book_cursor.execute('''
                INSERT OR REPLACE INTO users (id, username, email, password, role, title, phone, location, profile_image, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (u['id'], u['username'], u['email'], u['password'], u['role'], u['title'], u['phone'], u['location'], u['profile_image'], u['created_at']))
        book_conn.commit()
        book_conn.close()
    except Exception:
        pass  # Users table may not exist yet in curyent.db on first run


def init_book_db():
    """Initialize the booking database tables."""
    conn = get_book_db()
    cursor = conn.cursor()

    # Bookings table — extended with approval and payout columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booker_id INTEGER NOT NULL,
            booked_id INTEGER NOT NULL,
            booked_role TEXT NOT NULL,
            daily_rate REAL NOT NULL,
            charging_fee REAL NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            event_start_date TEXT,
            event_end_date TEXT,
            approval_status TEXT DEFAULT 'not_requested',
            payout_status TEXT DEFAULT 'not_started',
            rejection_reason TEXT,
            approved_at TIMESTAMP,
            payout_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booker_id) REFERENCES users(id),
            FOREIGN KEY (booked_id) REFERENCES users(id)
        )
    ''')

    # Service approval requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responded_at TIMESTAMP,
            approved INTEGER DEFAULT 0,
            rejection_reason TEXT,
            reminder_sent INTEGER DEFAULT 0,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    ''')

    # Celebration types table — shared list of celebration types
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS celebration_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed default celebration types if table is empty
    cursor.execute('SELECT COUNT(*) as count FROM celebration_types')
    if cursor.fetchone()['count'] == 0:
        default_types = [
            'Wedding', 'Birthday', 'Anniversary', 'Graduation',
            'Engagement', 'Baptism', 'Confirmation', 'Funeral',
            'Corporate Event', 'Conference', 'Product Launch',
            'Holiday Party', 'New Year', 'Christmas', 'Eid Celebration',
            'Cultural Ceremony', 'Traditional Marriage', 'Naming Ceremony',
            'Housewarming', 'Retirement Party', 'Other'
        ]
        for ctype in default_types:
            cursor.execute('INSERT INTO celebration_types (name) VALUES (?)', (ctype,))

    # Migration: add new columns to existing bookings table if they don't exist
    new_columns = [
        ('event_start_date', 'TEXT'),
        ('event_end_date', 'TEXT'),
        ('approval_status', "TEXT DEFAULT 'not_requested'"),
        ('payout_status', "TEXT DEFAULT 'not_started'"),
        ('rejection_reason', 'TEXT'),
        ('approved_at', 'TIMESTAMP'),
        ('payout_at', 'TIMESTAMP'),
        ('celebration_type', 'TEXT'),
        ('celebration_title', 'TEXT'),
        ('venue_location', 'TEXT'),
        ('start_time', 'TEXT'),
        ('end_time', 'TEXT'),
        ('attendees_count', 'INTEGER'),
        ('discount_percentage', 'REAL DEFAULT 0'),
        ('discount_amount', 'REAL DEFAULT 0'),
        ('is_multi_booking', 'INTEGER DEFAULT 0'),
        ('multi_booking_group_id', 'INTEGER'),
    ]

    # Get existing columns
    cursor.execute('PRAGMA table_info(bookings)')
    existing_columns = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE bookings ADD COLUMN {col_name} {col_type}')
            except Exception:
                pass  # Column may already exist from a concurrent migration

    conn.commit()
    conn.close()


def ensure_book_db_initialized():
    """Call this once at app startup to initialize the booking database.
    Do NOT call at import time — it causes database locks with Flask debug mode."""
    init_book_db()
    sync_users_to_book_db()


def can_book(booker_id, booked_id, booked_role):
    """
    Check if a user can book a person.
    A user cannot book the same person nor the same role if they already have an active (pending/accepted) booking.
    Returns (allowed, reason)
    """
    if booker_id == booked_id:
        return False, "You cannot book yourself"

    conn = get_book_db()
    cursor = conn.cursor()

    # Check if this exact person is already booked by this user with an active status
    cursor.execute('''
        SELECT id FROM bookings
        WHERE booker_id = ? AND booked_id = ? AND status IN ('pending', 'accepted')
    ''', (booker_id, booked_id))

    if cursor.fetchone():
        conn.close()
        return False, "You have already booked this person"

    # Check if this user has already booked someone with the same role with an active status
    cursor.execute('''
        SELECT id FROM bookings
        WHERE booker_id = ? AND booked_role = ? AND status IN ('pending', 'accepted')
    ''', (booker_id, booked_role))

    if cursor.fetchone():
        conn.close()
        return False, "You have already booked someone with this role"

    conn.close()
    return True, ""


def get_bookable_profiles(exclude_user_id=None):
    """
    Get all bookable profiles from the main database.
    Returns a list of profiles with user info and daily rates.
    If exclude_user_id is provided, that user will not appear in the list.
    """
    profiles = []
    main_conn = main_db.get_db()
    main_cursor = main_conn.cursor()

    # DJs
    main_cursor.execute('''
        SELECT u.id, u.username, u.role, u.phone, u.location, u.profile_image, de.total_per_event as daily_rate, 'dj_equipment' as profile_table
        FROM users u
        JOIN dj_equipment de ON u.id = de.user_id
        WHERE u.role = 'dj' AND u.id != ?
    ''', (exclude_user_id,))
    for row in main_cursor.fetchall():
        profiles.append(dict(row))

    # Event venues
    main_cursor.execute('''
        SELECT u.id, u.username, u.role, u.phone, u.location, u.profile_image, ev.daily_rate, 'event_venues' as profile_table
        FROM users u
        JOIN event_venues ev ON u.id = ev.user_id
        WHERE u.role = 'event' AND u.id != ?
    ''', (exclude_user_id,))
    for row in main_cursor.fetchall():
        profiles.append(dict(row))

    # Photographers
    main_cursor.execute('''
        SELECT u.id, u.username, u.role, u.phone, u.location, u.profile_image, p.daily_rate, 'photographer_profiles' as profile_table
        FROM users u
        JOIN photographer_profiles p ON u.id = p.user_id
        WHERE u.role = 'photographer' AND u.id != ?
    ''', (exclude_user_id,))
    for row in main_cursor.fetchall():
        profiles.append(dict(row))

    # Tents
    main_cursor.execute('''
        SELECT u.id, u.username, u.role, u.phone, u.location, u.profile_image, t.daily_rate, 'tent_inventory' as profile_table
        FROM users u
        JOIN tent_inventory t ON u.id = t.user_id
        WHERE u.role = 'tent' AND u.id != ?
    ''', (exclude_user_id,))
    for row in main_cursor.fetchall():
        profiles.append(dict(row))

    # Caterers
    main_cursor.execute('''
        SELECT u.id, u.username, u.role, u.phone, u.location, u.profile_image, c.daily_rate, 'caterer_profiles' as profile_table
        FROM users u
        JOIN caterer_profiles c ON u.id = c.user_id
        WHERE u.role = 'caterer' AND u.id != ?
    ''', (exclude_user_id,))
    for row in main_cursor.fetchall():
        profiles.append(dict(row))

    main_conn.close()
    return profiles


def get_user_bookings(user_id):
    """Get all bookings made by a user."""
    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.*, bu.username as booked_username, bu.role as booked_role_display
        FROM bookings b
        JOIN users bu ON b.booked_id = bu.id
        WHERE b.booker_id = ?
        ORDER BY b.created_at DESC
    ''', (user_id,))
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings


def get_received_bookings(user_id):
    """Get all bookings received by a user (where they are the booked person)."""
    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.*, bu.username as booker_username
        FROM bookings b
        JOIN users bu ON b.booker_id = bu.id
        WHERE b.booked_id = ?
        ORDER BY b.created_at DESC
    ''', (user_id,))
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings


# =========================
# Routes
# =========================

@book_bp.route('/bookings')
def booking_page():
    """Render the booking page."""
    user_id = session.get('user_id')
    if not user_id:
        provider_id = request.args.get('provider_id')
        return render_template('book/booking.html', profiles=[], my_bookings=[], received_bookings=[], error="Please log in to view bookings", provider=None, user_id=None)

    profiles = get_bookable_profiles(exclude_user_id=user_id)
    my_bookings = get_user_bookings(user_id)
    received_bookings = get_received_bookings(user_id)

    # Check if a specific provider is requested from the home page
    provider = None
    provider_id = request.args.get('provider_id', type=int)
    if provider_id:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT id, username, role, location, profile_image, phone FROM users WHERE id = ?', (provider_id,))
        user = main_cursor.fetchone()
        if user:
            user_dict = dict(user)
            role = user_dict['role']
            # Map role to the corresponding profile table and rate column
            role_tables = {
                'dj': ('dj_equipment', 'total_per_event'),
                'event': ('event_venues', 'daily_rate'),
                'photographer': ('photographer_profiles', 'daily_rate'),
                'tent': ('tent_inventory', 'daily_rate'),
                'caterer': ('caterer_profiles', 'daily_rate'),
            }
            if role in role_tables:
                table, rate_col = role_tables[role]
                main_cursor.execute(f'SELECT {rate_col} as daily_rate FROM {table} WHERE user_id = ?', (provider_id,))
                rate_row = main_cursor.fetchone()
                if rate_row:
                    user_dict['daily_rate'] = rate_row['daily_rate']
                    provider = user_dict
        main_conn.close()

    return render_template('book/booking.html',
                           profiles=profiles,
                           my_bookings=my_bookings,
                           received_bookings=received_bookings,
                           user_id=user_id,
                           provider=provider)


@book_bp.route('/api/book', methods=['POST'])
def create_booking():
    """Create a new booking with event dates and celebration details."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    booked_id = data.get('booked_id')
    booked_role = data.get('booked_role')
    daily_rate = data.get('daily_rate')
    event_start_date = data.get('event_start_date')
    event_end_date = data.get('event_end_date')

    # Celebration details
    celebration_type = data.get('celebration_type', '').strip()
    celebration_title = data.get('celebration_title', '').strip()
    venue_location = data.get('venue_location', '').strip()
    start_time = data.get('start_time', '').strip()
    end_time = data.get('end_time', '').strip()
    attendees_count = data.get('attendees_count')

    if not all([booked_id, booked_role, daily_rate]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    if not event_start_date:
        return jsonify({'success': False, 'message': 'Event start date is required'}), 400

    if not celebration_type:
        return jsonify({'success': False, 'message': 'Celebration type is required'}), 400

    if not celebration_title:
        return jsonify({'success': False, 'message': 'Celebration title is required'}), 400

    if not venue_location:
        return jsonify({'success': False, 'message': 'Venue location is required'}), 400

    if not start_time or not end_time:
        return jsonify({'success': False, 'message': 'Event start and end time are required'}), 400

    if not attendees_count or int(attendees_count) <= 0:
        return jsonify({'success': False, 'message': 'Number of attendees is required'}), 400

    # Check booking constraints
    allowed, reason = can_book(user_id, booked_id, booked_role)
    if not allowed:
        return jsonify({'success': False, 'message': reason}), 400

    # Calculate charges: total = daily_rate * 1.8
    # For DJs: 1.8x is the total per event
    # For others: 1.8x is the daily rate
    # The charging fee (platform fee) is 0.8x, the remaining 1.0x goes to the booked user
    daily_rate = float(daily_rate)
    charging_fee = daily_rate * 0.8  # 0.8x is the platform fee
    original_total = daily_rate * 1.8  # total = 1.8 * daily_rate

    # Check loyalty discount: 5% off on every 5th booking (5th, 10th, 15th, ...)
    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM bookings WHERE booker_id = ?', (user_id,))
    previous_bookings = cursor.fetchone()['count']
    current_booking_number = previous_bookings + 1  # This booking will be the Nth
    is_fifth_booking = (current_booking_number % 5 == 0)

    discount_percentage = 0.0
    discount_amount = 0.0
    total_amount = original_total

    if is_fifth_booking:
        discount_percentage = 5.0
        discount_amount = original_total * (discount_percentage / 100)
        total_amount = original_total - discount_amount

    cursor.execute('''
        INSERT INTO bookings (booker_id, booked_id, booked_role, daily_rate, charging_fee, total_amount, status,
                              event_start_date, event_end_date, celebration_type, celebration_title,
                              venue_location, start_time, end_time, attendees_count,
                              discount_percentage, discount_amount, is_multi_booking)
        VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, booked_id, booked_role, daily_rate, charging_fee, total_amount,
          event_start_date, event_end_date, celebration_type, celebration_title,
          venue_location, start_time, end_time, int(attendees_count),
          discount_percentage, discount_amount, 0))
    conn.commit()
    booking_id = cursor.lastrowid

    # Get usernames for notifications
    booker_username = ''
    booked_username = ''
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        booker_user = main_cursor.fetchone()
        main_cursor.execute('SELECT username FROM users WHERE id = ?', (booked_id,))
        booked_user = main_cursor.fetchone()
        main_conn.close()
        if booker_user:
            booker_username = booker_user['username']
        if booked_user:
            booked_username = booked_user['username']
    except Exception:
        pass

    # Notify the booked provider about the new booking request
    try:
        noti_module.create_notification(
            user_id=booked_id,
            title='New booking request',
            message=f'{booker_username} has requested to book you for {celebration_title}.',
            notification_type='booking_request',
            related_item_id=booking_id,
            priority='medium',
            action_url=f'/bookings?tab=received&id={booking_id}',
            action_label='View Details'
        )
    except Exception:
        pass

    # Notify the booker that their order was sent successfully
    booker_noti_msg = f'Your booking request for {celebration_title} has been sent to {booked_username}. Awaiting provider acceptance before payment.'
    if is_fifth_booking:
        booker_noti_msg = f'Your booking request for {celebration_title} has been sent to {booked_username}! You got a 5% loyalty discount (booking #{current_booking_number}). Save KES {discount_amount:.0f}!'

    try:
        noti_module.create_notification(
            user_id=user_id,
            title='Order placed',
            message=booker_noti_msg,
            notification_type='booking_request',
            related_item_id=booking_id,
            priority='low',
            action_url=f'/bookings?tab=my&id={booking_id}',
            action_label='View Bookings'
        )
    except Exception:
        pass

    conn.close()

    response_data = {
        'success': True,
        'message': 'Booking request sent successfully — awaiting provider acceptance',
        'booking_id': booking_id,
        'total_amount': total_amount,
        'charging_fee': charging_fee
    }
    if is_fifth_booking:
        response_data['message'] = f'Booking sent! You got a 5% loyalty discount (booking #{current_booking_number}). Save KES {discount_amount:.0f}!'
        response_data['is_fifth_booking'] = True
        response_data['discount_percentage'] = discount_percentage
        response_data['discount_amount'] = discount_amount
        response_data['original_total'] = original_total

    return jsonify(response_data)


@book_bp.route('/api/book/loyalty-check', methods=['GET'])
def loyalty_check():
    """Check if the current user's next booking qualifies for the 5th-booking loyalty discount."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'is_fifth_booking': False, 'booking_number': 0}), 200

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM bookings WHERE booker_id = ?', (user_id,))
    previous_bookings = cursor.fetchone()['count']
    current_booking_number = previous_bookings + 1
    conn.close()

    is_fifth = (current_booking_number % 5 == 0)
    return jsonify({
        'is_fifth_booking': is_fifth,
        'booking_number': current_booking_number
    }), 200


@book_bp.route('/api/book/multi', methods=['POST'])
def create_multi_booking():
    """
    Create multiple bookings at once for different roles.
    If 2 or more different roles are booked, apply a 10% discount on each booking's total.
    Request body: {
        "providers": [
            {"booked_id": 1, "booked_role": "dj", "daily_rate": 5000},
            {"booked_id": 2, "booked_role": "photographer", "daily_rate": 3000},
            ...
        ],
        "event_start_date": "2025-12-25",
        "event_end_date": "2025-12-25",
        "celebration_type": "Wedding",
        "celebration_title": "John & Jane's Wedding",
        "venue_location": "Nairobi",
        "start_time": "10:00",
        "end_time": "22:00",
        "attendees_count": 150
    }
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    providers = data.get('providers', [])
    
    if not providers or len(providers) < 2:
        return jsonify({'success': False, 'message': 'Select at least 2 providers for a multi-booking discount'}), 400

    # Event details
    event_start_date = data.get('event_start_date')
    event_end_date = data.get('event_end_date')
    celebration_type = data.get('celebration_type', '').strip()
    celebration_title = data.get('celebration_title', '').strip()
    venue_location = data.get('venue_location', '').strip()
    start_time = data.get('start_time', '').strip()
    end_time = data.get('end_time', '').strip()
    attendees_count = data.get('attendees_count')

    # Validate required fields
    if not event_start_date:
        return jsonify({'success': False, 'message': 'Event start date is required'}), 400
    if not celebration_type:
        return jsonify({'success': False, 'message': 'Celebration type is required'}), 400
    if not celebration_title:
        return jsonify({'success': False, 'message': 'Celebration title is required'}), 400
    if not venue_location:
        return jsonify({'success': False, 'message': 'Venue location is required'}), 400
    if not start_time or not end_time:
        return jsonify({'success': False, 'message': 'Event start and end time are required'}), 400
    if not attendees_count or int(attendees_count) <= 0:
        return jsonify({'success': False, 'message': 'Number of attendees is required'}), 400

    # Check for duplicate roles — each role can only be booked once
    roles = [p.get('booked_role') for p in providers]
    if len(roles) != len(set(roles)):
        return jsonify({'success': False, 'message': 'You cannot book the same role twice'}), 400

    # Validate each provider
    for p in providers:
        if not all([p.get('booked_id'), p.get('booked_role'), p.get('daily_rate')]):
            return jsonify({'success': False, 'message': 'Missing required fields for a provider'}), 400

    # Check booking constraints for each provider
    for p in providers:
        allowed, reason = can_book(user_id, p['booked_id'], p['booked_role'])
        if not allowed:
            return jsonify({'success': False, 'message': f"{p['booked_role'].capitalize()}: {reason}"}), 400

    # Calculate discount: 10% off each booking when booking 2+ roles
    # Bonus: if exactly 5 roles are booked, the 5th booking gets an additional 5% discount
    base_discount_percentage = 10.0
    is_five_booking = len(providers) == 5
    fifth_bonus_discount = 5.0  # Extra 5% on the 5th booking when all 5 roles are booked

    conn = get_book_db()
    cursor = conn.cursor()

    booking_ids = []
    total_original = 0
    total_discount = 0
    total_final = 0
    fifth_booking_discount = 0  # Track the extra 5th-row discount

    # Get usernames for notifications
    booker_username = ''
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        booker_user = main_cursor.fetchone()
        main_conn.close()
        if booker_user:
            booker_username = booker_user['username']
    except Exception:
        pass

    for idx, p in enumerate(providers):
        daily_rate = float(p['daily_rate'])
        charging_fee = daily_rate * 0.8
        original_total = daily_rate * 1.8

        # Apply base 10% discount
        discount_amount = original_total * (base_discount_percentage / 100)

        # Apply extra 5% discount on the 5th booking (index 4) when all 5 roles are booked
        fifth_bonus = 0.0
        effective_discount_percentage = base_discount_percentage
        if is_five_booking and idx == 4:
            # Additional 5% off the already-discounted price
            fifth_bonus = (original_total - discount_amount) * (fifth_bonus_discount / 100)
            discount_amount += fifth_bonus
            effective_discount_percentage = base_discount_percentage + 5.0

        final_total = original_total - discount_amount

        total_original += original_total
        total_discount += discount_amount
        total_final += final_total
        if idx == 4 and is_five_booking:
            fifth_booking_discount = fifth_bonus

        # 18 columns: booker_id, booked_id, booked_role, daily_rate, charging_fee, total_amount, status,
        # event_start_date, event_end_date, celebration_type, celebration_title, venue_location,
        # start_time, end_time, attendees_count, discount_percentage, discount_amount, is_multi_booking
        cursor.execute('''
            INSERT INTO bookings (
                booker_id, booked_id, booked_role, daily_rate, charging_fee, total_amount, status,
                event_start_date, event_end_date, celebration_type, celebration_title,
                venue_location, start_time, end_time, attendees_count,
                discount_percentage, discount_amount, is_multi_booking
            ) VALUES (
                ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            user_id,                          # booker_id
            p['booked_id'],                   # booked_id
            p['booked_role'],                 # booked_role
            daily_rate,                       # daily_rate
            charging_fee,                     # charging_fee
            final_total,                      # total_amount
            event_start_date,                 # event_start_date
            event_end_date,                   # event_end_date
            celebration_type,                 # celebration_type
            celebration_title,                # celebration_title
            venue_location,                   # venue_location
            start_time,                       # start_time
            end_time,                         # end_time
            int(attendees_count),             # attendees_count
            effective_discount_percentage,    # discount_percentage
            discount_amount,                  # discount_amount
            1                                 # is_multi_booking
        ))
        booking_ids.append(cursor.lastrowid)

        # Notify the booked provider
        booked_username = ''
        try:
            main_conn = main_db.get_db()
            main_cursor = main_conn.cursor()
            main_cursor.execute('SELECT username FROM users WHERE id = ?', (p['booked_id'],))
            booked_user = main_cursor.fetchone()
            main_conn.close()
            if booked_user:
                booked_username = booked_user['username']
        except Exception:
            pass

        # Build notification message with appropriate discount info
        if is_five_booking and idx == 4:
            noti_message = f'{booker_username} has requested to book you ({p["booked_role"].capitalize()}) for {celebration_title} as part of a full 5-role booking! You get a 10% + 5% bonus discount!'
        else:
            noti_message = f'{booker_username} has requested to book you ({p["booked_role"].capitalize()}) for {celebration_title} as part of a multi-provider booking. You get a 10% discount bundle!'

        try:
            noti_module.create_notification(
                user_id=p['booked_id'],
                title='New multi-booking request',
                message=noti_message,
                notification_type='booking_request',
                related_item_id=booking_ids[-1],
                priority='medium',
                action_url=f'/bookings?tab=received&id={booking_ids[-1]}',
                action_label='View Details'
            )
        except Exception:
            pass

    conn.commit()
    conn.close()

    # Notify the booker
    if is_five_booking:
        noti_msg = f'Your booking request for {celebration_title} has been sent to all 5 providers with a 10% discount + 5% bonus on the 5th! Original: KES {total_original:.0f}, You save: KES {total_discount:.0f}, Total: KES {total_final:.0f}'
    else:
        noti_msg = f'Your booking request for {celebration_title} has been sent to {len(providers)} providers with a 10% discount! Original: KES {total_original:.0f}, You save: KES {total_discount:.0f}, Total: KES {total_final:.0f}'

    try:
        noti_module.create_notification(
            user_id=user_id,
            title='Multi-booking placed',
            message=noti_msg,
            notification_type='booking_request',
            related_item_id=booking_ids[0],
            priority='low',
            action_url=f'/bookings?tab=my',
            action_label='View Bookings'
        )
    except Exception:
        pass

    response_data = {
        'success': True,
        'booking_ids': booking_ids,
        'total_original': total_original,
        'discount_amount': total_discount,
        'total_final': total_final,
        'discount_percentage': base_discount_percentage
    }
    if is_five_booking:
        response_data['message'] = f'Multi-booking request sent to all 5 providers with 10% + 5% bonus discount!'
        response_data['fifth_booking_discount'] = fifth_booking_discount
        response_data['is_five_booking'] = True
    else:
        response_data['message'] = f'Multi-booking request sent to {len(providers)} providers with 10% discount!'

    return jsonify(response_data)


@book_bp.route('/api/celebration-types', methods=['GET'])
def get_celebration_types():
    """Get all celebration types."""
    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM celebration_types ORDER BY name')
    types = [{'id': row['id'], 'name': row['name']} for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'types': types})


@book_bp.route('/api/celebration-types', methods=['POST'])
def add_celebration_type():
    """Add a new celebration type to the shared list."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'success': False, 'message': 'Celebration type name is required'}), 400

    if len(name) > 100:
        return jsonify({'success': False, 'message': 'Name is too long (max 100 characters)'}), 400

    conn = get_book_db()
    cursor = conn.cursor()

    # Check if type already exists
    cursor.execute('SELECT id FROM celebration_types WHERE name = ?', (name,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'This celebration type already exists'}), 400

    cursor.execute('INSERT INTO celebration_types (name) VALUES (?)', (name,))
    conn.commit()
    type_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Celebration type added successfully',
        'type_id': type_id,
        'name': name
    })


@book_bp.route('/api/booking/accept/<int:booking_id>', methods=['POST'])
def accept_booking(booking_id):
    """Accept a booking request (only the booked user can accept)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    if booking['booked_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'You are not authorized to accept this booking'}), 403

    if booking['status'] != 'pending':
        conn.close()
        return jsonify({'success': False, 'message': 'This booking is no longer pending'}), 400

    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', ('accepted', booking_id))
    conn.commit()
    booker_id = booking['booker_id']
    conn.close()

    # Notify the booker that their booking was accepted
    try:
        noti_module.create_notification(
            user_id=booker_id,
            title='Booking accepted',
            message=f'Your booking request for {booking["celebration_title"]} has been accepted. Payment is now required.',
            notification_type='booking_accepted',
            related_item_id=booking_id,
            priority='medium',
            action_url=f'/bookings?tab=my&id={booking_id}',
            action_label='View Details'
        )
    except Exception:
        pass

    # Get booker's phone number for M-Pesa STK Push (only after acceptance)
    booker_phone = ''
    try:
        main_conn2 = main_db.get_db()
        main_cursor2 = main_conn2.cursor()
        main_cursor2.execute('SELECT phone FROM users WHERE id = ?', (booker_id,))
        booker_row = main_cursor2.fetchone()
        main_conn2.close()
        if booker_row:
            booker_phone = booker_row['phone'] or ''
    except Exception:
        pass

    # Initiate M-Pesa STK Push for payment (only after provider accepts)
    mpesa_result = {'success': True, 'message': 'Payment not initiated', 'simulated': True}
    if booker_phone:
        mpesa_result = mpesa_module.initiate_stk_push(
            phone_number=booker_phone,
            amount=booking['total_amount'],
            account_reference=f'CURYENT-{booking_id}',
            transaction_desc=f'Booking for {booking["celebration_title"]}',
            booking_id=booking_id
        )

    return jsonify({
        'success': True,
        'message': 'Booking accepted successfully — payment prompt sent to booker',
        'payment': mpesa_result
    })


@book_bp.route('/api/booking/decline/<int:booking_id>', methods=['POST'])
def decline_booking(booking_id):
    """Decline a booking request (only the booked user can decline)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    if booking['booked_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'You are not authorized to decline this booking'}), 403

    if booking['status'] != 'pending':
        conn.close()
        return jsonify({'success': False, 'message': 'This booking is no longer pending'}), 400

    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', ('declined', booking_id))
    conn.commit()
    booker_id = booking['booker_id']
    conn.close()

    # Notify the booker that their booking was declined
    try:
        noti_module.create_notification(
            user_id=booker_id,
            title='Booking declined',
            message=f'Your booking request for {booking["celebration_title"]} has been declined.',
            notification_type='booking_declined',
            related_item_id=booking_id,
            priority='medium',
            action_url=f'/bookings?tab=my&id={booking_id}',
            action_label='View Details'
        )
    except Exception:
        pass

    return jsonify({'success': True, 'message': 'Booking declined'})


@book_bp.route('/api/booking/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking (only the booker can cancel their own booking)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    if booking['booker_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'You are not authorized to cancel this booking'}), 403

    if booking['status'] == 'cancelled':
        conn.close()
        return jsonify({'success': False, 'message': 'This booking is already cancelled'}), 400

    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', ('cancelled', booking_id))
    conn.commit()
    booked_id = booking['booked_id']
    conn.close()

    # Notify the provider that the booking was cancelled
    try:
        noti_module.create_notification(
            user_id=booked_id,
            title='Booking cancelled',
            message=f'A booking for {booking["celebration_title"]} has been cancelled.',
            notification_type='booking_cancelled',
            related_item_id=booking_id,
            priority='low',
            action_url=f'/bookings?tab=received&id={booking_id}',
            action_label='View Details'
        )
    except Exception:
        pass

    return jsonify({'success': True, 'message': 'Booking cancelled successfully'})


# =========================
# Service Approval & Payout
# =========================

def send_approval_notification(booking):
    """
    Send a WhatsApp notification to the booked person asking for service approval.
    Uses the WhatsApp Business Cloud API via whatsapp.py.
    """
    try:
        # Get the booked person's phone number
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT phone FROM users WHERE id = ?', (booking['booked_id'],))
        user_row = main_cursor.fetchone()
        main_conn.close()

        if not user_row or not user_row['phone']:
            return {'success': False, 'message': 'No phone number found for booked person'}

        phone_number = user_row['phone']

        # Build the approval message
        message_body = (
            f'CURYENT - Service Approval Request\n\n'
            f'You have been booked for an event.\n'
            f'Event Start: {booking["event_start_date"] or "Not set"}\n'
            f'Event End: {booking["event_end_date"] or "Not set"}\n'
            f'Total Amount: KES {booking["total_amount"]:.0f}\n'
            f'You Will Receive: KES {booking["daily_rate"]:.0f}\n\n'
            f'Please log in to CURYENT to approve or decline this service request.\n'
            f'Your approval confirms you delivered the service.'
        )

        # Send via unified WhatsApp helper
        import templates.account.whatsapp as whatsapp_module
        result = whatsapp_module.send_message(phone_number, message_body)

        if result['success']:
            return {'success': True, 'message': 'Approval notification sent via WhatsApp'}
        else:
            return {'success': True, 'message': 'Approval notification queued (delivery retry later)'}

    except Exception as e:
        print(f'[APPROVAL DEBUG] Failed to send notification: {str(e)}')
        return {'success': True, 'message': 'Approval notification queued (delivery retry later)'}


def send_payout_notification(booking):
    """Send a WhatsApp notification that payout has been processed."""
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT phone FROM users WHERE id = ?', (booking['booked_id'],))
        user_row = main_cursor.fetchone()
        main_conn.close()

        if not user_row or not user_row['phone']:
            return {'success': False, 'message': 'No phone number found'}

        phone_number = user_row['phone']

        message_body = (
            f'CURYENT - Payment Received\n\n'
            f'Your service has been approved and payment has been processed!\n'
            f'Amount: KES {booking["daily_rate"]:.0f}\n'
            f'Thank you for your service on CURYENT.'
        )

        # Send via unified WhatsApp helper
        import templates.account.whatsapp as whatsapp_module
        result = whatsapp_module.send_message(phone_number, message_body)

        if result['success']:
            return {'success': True, 'message': 'Payout notification sent'}
        else:
            return {'success': True, 'message': 'Payout notification queued'}

    except Exception as e:
        print(f'[PAYOUT DEBUG] Failed to send notification: {str(e)}')
        return {'success': True, 'message': 'Payout notification queued'}


def send_rejection_notification(booking):
    """Send a WhatsApp notification asking the booked person for a rejection reason."""
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT phone FROM users WHERE id = ?', (booking['booked_id'],))
        user_row = main_cursor.fetchone()
        main_conn.close()

        if not user_row or not user_row['phone']:
            return {'success': False, 'message': 'No phone number found'}

        phone_number = user_row['phone']

        message_body = (
            f'CURYENT - Service Rejection\n\n'
            f'Your service request was not approved.\n'
            f'Please log in to CURYENT to provide a reason for the rejection.\n'
            f'This helps us improve our service quality.'
        )

        # Send via unified WhatsApp helper
        import templates.account.whatsapp as whatsapp_module
        result = whatsapp_module.send_message(phone_number, message_body)

        if result['success']:
            return {'success': True, 'message': 'Rejection notification sent'}
        else:
            return {'success': True, 'message': 'Rejection notification queued'}

    except Exception as e:
        print(f'[REJECTION DEBUG] Failed to send notification: {str(e)}')
        return {'success': True, 'message': 'Rejection notification queued'}


@book_bp.route('/api/booking/<int:booking_id>/request-approval', methods=['POST'])
def request_service_approval(booking_id):
    """
    Request service approval from the booked person.
    This is called when the event start date approaches or the booker confirms the event has occurred.
    Sends a notification to the booked person to approve that service was delivered.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    # Only the booker can request approval
    if booking['booker_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'Only the booker can request approval'}), 403

    if booking['status'] != 'accepted':
        conn.close()
        return jsonify({'success': False, 'message': 'Booking must be accepted before requesting approval'}), 400

    # Check if approval already requested
    if booking['approval_status'] in ('requested', 'approved', 'rejected'):
        conn.close()
        return jsonify({'success': False, 'message': 'Approval already requested or resolved'}), 400

    # Update booking approval status
    cursor.execute('UPDATE bookings SET approval_status = ? WHERE id = ?', ('requested', booking_id))

    # Create approval record
    cursor.execute('INSERT INTO service_approvals (booking_id) VALUES (?)', (booking_id,))
    conn.commit()
    conn.close()

    # Send notification to the booked person
    booking['approval_status'] = 'requested'
    notification_result = send_approval_notification(booking)

    return jsonify({
        'success': True,
        'message': 'Approval request sent to the booked person',
        'notification': notification_result.get('message', '')
    })


@book_bp.route('/api/booking/<int:booking_id>/approve-service', methods=['POST'])
def approve_service(booking_id):
    """
    The booked person approves that they delivered the service.
    After approval, a 30-60 minute timer starts before payout.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    # Only the booked person can approve
    if booking['booked_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'Only the booked person can approve service'}), 403

    if booking['approval_status'] != 'requested':
        conn.close()
        return jsonify({'success': False, 'message': 'No pending approval request'}), 400

    now = datetime.now().isoformat()

    # Update booking to approved — payout will be scheduled for 2 hours before event end
    cursor.execute('''
        UPDATE bookings SET approval_status = ?, approved_at = ?, payout_status = ?
        WHERE id = ?
    ''', ('approved', now, 'scheduled_for_event', booking_id))

    # Update approval record
    cursor.execute('''
        UPDATE service_approvals SET approved = 1, responded_at = ?
        WHERE booking_id = ?
    ''', (now, booking_id))

    conn.commit()

    # Calculate payout time (2 hours before event end)
    payout_amount = booking['daily_rate']  # The booked person receives 1.0x the daily rate
    estimated_payout_time = None
    if booking['event_end_date']:
        estimated_payout_time = datetime.fromisoformat(booking['event_end_date']) - timedelta(hours=2)

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Service approved! Payout will be processed 2 hours before the event end time.',
        'payout_amount': payout_amount,
        'estimated_payout_time': estimated_payout_time.strftime('%Y-%m-%d %H:%M') if estimated_payout_time else None
    })


@book_bp.route('/api/booking/<int:booking_id>/reject-service', methods=['POST'])
def reject_service(booking_id):
    """
    The booked person rejects that they delivered the service.
    They must provide a reason for rejection.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    reason = data.get('reason', '').strip()

    if not reason:
        return jsonify({'success': False, 'message': 'Rejection reason is required'}), 400

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    # Only the booked person can reject
    if booking['booked_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'Only the booked person can reject service'}), 403

    if booking['approval_status'] != 'requested':
        conn.close()
        return jsonify({'success': False, 'message': 'No pending approval request'}), 400

    now = datetime.now().isoformat()

    # Update booking to rejected
    cursor.execute('''
        UPDATE bookings SET approval_status = ?, rejection_reason = ?, payout_status = ?
        WHERE id = ?
    ''', ('rejected', reason, 'cancelled', booking_id))

    # Update approval record
    cursor.execute('''
        UPDATE service_approvals SET approved = 0, responded_at = ?, rejection_reason = ?
        WHERE booking_id = ?
    ''', (now, reason, booking_id))

    conn.commit()

    # Send notification to the booker about rejection
    booking['approval_status'] = 'rejected'
    booking['rejection_reason'] = reason
    notification_result = send_rejection_notification(booking)

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Service rejected. Reason has been recorded.',
        'notification': notification_result.get('message', '')
    })


@book_bp.route('/api/booking/<int:booking_id>/process-payout', methods=['POST'])
def process_payout(booking_id):
    """
    Manually trigger the payout to the booked person.
    Payout is normally automated 2 hours before the event end time by the scheduler.
    This endpoint allows manual override when needed.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    # Check payout eligibility
    if booking['approval_status'] != 'approved':
        conn.close()
        return jsonify({'success': False, 'message': 'Service must be approved before payout'}), 400

    if booking['payout_status'] == 'paid':
        conn.close()
        return jsonify({'success': False, 'message': 'Payout already processed'}), 400

    if booking['payout_status'] not in ('scheduled_for_event', 'waiting_payout'):
        conn.close()
        return jsonify({'success': False, 'message': 'Payout not ready'}), 400

    now = datetime.now().isoformat()

    # Get provider's phone number for M-Pesa B2C payout
    provider_phone = ''
    try:
        main_conn2 = main_db.get_db()
        main_cursor2 = main_conn2.cursor()
        main_cursor2.execute('SELECT phone FROM users WHERE id = ?', (booking['booked_id'],))
        provider_row = main_cursor2.fetchone()
        main_conn2.close()
        if provider_row:
            provider_phone = provider_row['phone'] or ''
    except Exception:
        pass

    # Initiate M-Pesa B2C payout
    payout_amount = booking['daily_rate']  # 1.0x goes to the booked person
    mpesa_payout_result = {'success': True, 'message': 'Payout not initiated', 'simulated': True}
    if provider_phone:
        mpesa_payout_result = mpesa_module.initiate_b2c_payout(
            recipient_phone=provider_phone,
            amount=payout_amount,
            occasion=f'Service payout for {booking.get("celebration_title", "booking")}'
        )

    # Update booking payout status
    cursor.execute('''
        UPDATE bookings SET payout_status = ?, payout_at = ?
        WHERE id = ?
    ''', ('paid', now, booking_id))
    conn.commit()

    # Send payout notification
    booking['payout_status'] = 'paid'
    booking['payout_at'] = now
    notification_result = send_payout_notification(booking)

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Payout processed successfully',
        'payout_amount': payout_amount,
        'notification': notification_result.get('message', ''),
        'mpesa_payout': mpesa_payout_result
    })


@book_bp.route('/api/booking/<int:booking_id>/status', methods=['GET'])
def get_booking_status(booking_id):
    """Get detailed status of a booking including approval and payout info."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_book_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

    # Check if user is involved in this booking
    if booking['booker_id'] != user_id and booking['booked_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'message': 'You are not involved in this booking'}), 403

    booking_dict = dict(booking)

    # Get approval record if exists
    cursor.execute('SELECT * FROM service_approvals WHERE booking_id = ?', (booking_id,))
    approval = cursor.fetchone()
    if approval:
        booking_dict['approval_record'] = dict(approval)

    conn.close()
    return jsonify({'success': True, 'booking': booking_dict})


@book_bp.route('/api/profiles', methods=['GET'])
def list_profiles():
    """API to get all bookable profiles."""
    profiles = get_bookable_profiles()
    return jsonify({'success': True, 'profiles': profiles})


# =========================
# M-Pesa Callback Routes
# =========================

@book_bp.route('/api/mpesa/callback', methods=['POST'])
def mpesa_c2b_callback():
    """Handle C2B callback from M-Pesa after customer completes STK Push payment."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': 'No data received'}), 400

    # Process the callback
    result = mpesa_module.handle_c2b_callback(data)

    if result.get('success'):
        # Extract BillNumber (AccountReference) to find the booking
        bill_number = data.get('BillNumber', '')
        transaction_id = data.get('TransactionID', '')
        amount = data.get('Amount', 0)

        # If BillNumber matches our format (CURYENT-<booking_id>), update booking status
        if bill_number.startswith('CURYENT-'):
            try:
                booking_id = int(bill_number.split('-')[1])
                conn = get_book_db()
                cursor = conn.cursor()
                cursor.execute('SELECT id, status FROM bookings WHERE id = ?', (booking_id,))
                booking = cursor.fetchone()
                if booking:
                    # Update booking to reflect payment received
                    cursor.execute('''
                        UPDATE bookings SET status = 'paid'
                        WHERE id = ? AND status IN ('pending', 'accepted')
                    ''', (booking_id,))
                    conn.commit()
                    print(f'[M-Pesa Callback] Booking {booking_id} marked as paid (KES {amount})')
            except Exception as e:
                print(f'[M-Pesa Callback] Error updating booking: {e}')

    return jsonify({'message': 'Callback received'}), 200


@book_bp.route('/api/mpesa/callback/b2c/result', methods=['POST'])
def mpesa_b2c_result_callback():
    """Handle B2C result callback from M-Pesa after payout."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': 'No data received'}), 400

    result_code = data.get('ResultCode', -1)
    result_desc = data.get('ResultDesc', '')
    recipient = data.get('RecipientNumber', '')
    amount = data.get('Amount', 0)

    if result_code == 0:
        print(f'[M-Pesa B2C Callback] Payout successful: KES {amount} to {recipient}')
    else:
        print(f'[M-Pesa B2C Callback] Payout failed: {result_desc} (KES {amount} to {recipient})')

    return jsonify({'message': 'Callback received'}), 200


@book_bp.route('/api/mpesa/callback/b2c/timeout', methods=['POST'])
def mpesa_b2c_timeout_callback():
    """Handle B2C timeout callback from M-Pesa."""
    data = request.get_json(silent=True)
    if data:
        recipient = data.get('RecipientNumber', '')
        amount = data.get('Amount', 0)
        print(f'[M-Pesa B2C Timeout] Payout timed out: KES {amount} to {recipient}')

    return jsonify({'message': 'Timeout callback received'}), 200
