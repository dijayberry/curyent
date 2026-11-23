"""
One-time script to create 120 sample users for demo purposes.
Creates 20 users per role: client, dj, photographer, venue, tent, caterer.
All users share the password: curyent2024

Run this in the PythonAnywhere Bash console:
    cd /home/dijayberry/curyent
    python create_sample_users.py
"""
import sqlite3
import os
from datetime import datetime

# Database paths
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')
social_db = os.path.join(base_dir, 'social.db')

PASSWORD = 'curyent2024'

# Sample data for each role
client_names = [
    'alex', 'sarah', 'mike', 'emma', 'james', 'olivia', 'david', 'sophia',
    'robert', 'isabella', 'john', 'mia', 'william', 'charlotte', 'richard',
    'amelia', 'thomas', 'harper', 'daniel', 'evelyn'
]

dj_names = [
    'beats', 'mixmaster', 'spinmaster', 'bassdrop', 'soundwave', 'rhythmking',
    'turntable', 'vinylvibes', 'groovebox', 'pulsebeats', 'nightowl', 'djflash',
    'electrobeat', 'soundcloud', 'mixwizard', 'beatmaker', 'djstorm', 'vibesound',
    'rhythmrush', 'djnova'
]

photo_names = [
    'lens', 'shutter', 'capture', 'focus', 'aperture', 'pixel', 'snapshot',
    'portrait', 'landscape', 'macroshot', 'lightroom', 'rawphoto', 'clickshot',
    'framemaster', 'visionary', 'lenscraft', 'photovibe', 'imagepro', 'snapart',
    'picperfect'
]

# Venues — realistic business names (hotels, gardens, resorts, lodges, event halls)
venue_names = [
    'Mark Hotel', 'Olives Garden', 'Sunset Resort', 'Royal Lodge', 'Grand Ballroom',
    'Emerald Gardens', 'Skyline Hotel', 'Lakeside Resort', 'Palm Beach Hotel',
    'Heritage Lodge', 'Crystal Hall', 'Golden Acres', 'Sunrise Garden',
    'The Grand Pavilion', 'Olive Tree Resort', 'Marigold Hotel', 'Savanna Lodge',
    'Blue Waters Resort', 'Crown Gardens', 'Elegance Hall'
]

# Tents — realistic business names (marquee, event setup companies)
tent_names = [
    'Royal Marquee', 'Elegant Canopy', 'Grand Tent Co', 'Celestial Events',
    'Prestige Tents', 'Golden Marquee', 'Luxury Canopy', 'Crystal Dome',
    'Sunrise Tents', 'Emerald Pavilion', 'Skyline Marquee', 'Heritage Tents',
    'Olive Branch Events', 'Savanna Marquee', 'Blue Sky Tents',
    'Crown Canopy', 'Golden Gate Tents', 'Sunset Marquee', 'Pearl Pavilion',
    'Diamond Tents'
]

# Caterers — realistic business names
cater_names = [
    'Delight Catering', 'Flavor Kitchen', 'Taste Bites', 'Gourmet Delights',
    'Savory Feasts', 'Sweet Banquets', 'Feast Masters', 'Banquet Royale',
    'Cuisine Kings', 'Delicacy Dishes', 'Epicure Table', 'Palate Catering',
    'Nosh Kitchen', 'Dine Elegance', 'Savor Foods', 'Relish Catering',
    'Banquet Pro', 'Foodie Delights', 'Chefs Table', 'TasteBud Catering'
]

locations = [
    'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika', 'Nyeri',
    'Malindi', 'Nanyuki', 'Kitale', 'Garissa', 'Kakamega', 'Bungoma',
    'Meru', 'Embu', 'Machakos', 'Kajiado', 'Kiambu', 'Uasin Gishu', 'Nandi'
]


def create_users_in_db(db_path, db_name):
    """Create sample users in a given database."""
    print(f"Creating users in {db_name}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure users table exists
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
    conn.commit()

    created = 0
    skipped = 0

    # Clients
    for i, name in enumerate(client_names):
        username = name
        email = f"{name}@curyent.com"
        phone = f"+2547{100000000 + i}"
        location = locations[i % len(locations)]
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, role, phone, location)
                VALUES (?, ?, ?, 'client', ?, ?)
            ''', (username, email, PASSWORD, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    # DJs
    for i, name in enumerate(dj_names):
        username = f"dj_{name}"
        email = f"{name}@curyent.com"
        title = f"Professional DJ - {name.title()}"
        phone = f"+2547{200000000 + i}"
        location = locations[i % len(locations)]
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, role, title, phone, location)
                VALUES (?, ?, ?, 'dj', ?, ?, ?)
            ''', (username, email, PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    # Photographers
    for i, name in enumerate(photo_names):
        username = f"photo_{name}"
        email = f"{name}@curyent.com"
        title = f"Event Photographer - {name.title()}"
        phone = f"+2547{300000000 + i}"
        location = locations[i % len(locations)]
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, role, title, phone, location)
                VALUES (?, ?, ?, 'photographer', ?, ?, ?)
            ''', (username, email, PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    # Venues
    for i, name in enumerate(venue_names):
        username = name.replace(' ', '_').lower()
        email = f"{name.replace(' ', '').lower()}@curyent.com"
        title = f"{name} — Event Venue"
        phone = f"+2547{400000000 + i}"
        location = locations[i % len(locations)]
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, role, title, phone, location)
                VALUES (?, ?, ?, 'venue', ?, ?, ?)
            ''', (username, email, PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    # Tents
    for i, name in enumerate(tent_names):
        username = name.replace(' ', '_').lower()
        email = f"{name.replace(' ', '').lower()}@curyent.com"
        title = f"{name} — Tent Services"
        phone = f"+2547{500000000 + i}"
        location = locations[i % len(locations)]
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, role, title, phone, location)
                VALUES (?, ?, ?, 'tent', ?, ?, ?)
            ''', (username, email, PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    # Caterers
    for i, name in enumerate(cater_names):
        username = name.replace(' ', '_').replace("'", '').lower()
        email = f"{name.replace(' ', '').replace("'", '').lower()}@curyent.com"
        title = f"{name} — Catering Services"
        phone = f"+2547{600000000 + i}"
        location = locations[i % len(locations)]
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, role, title, phone, location)
                VALUES (?, ?, ?, 'caterer', ?, ?, ?)
            ''', (username, email, PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"  {db_name}: {created} created, {skipped} skipped (already existed)")
    return created


def create_role_profiles():
    """Create role-specific profiles in probase.db."""
    print("\nCreating role-specific profiles in probase.db...")
    conn = sqlite3.connect(probase_db)
    cursor = conn.cursor()

    # DJ Equipment profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dj_equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            equipment TEXT,
            total_per_event REAL DEFAULT 5000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Photographer profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photographer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            specialization TEXT,
            daily_rate REAL DEFAULT 3000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Venue profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venue_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            capacity INTEGER DEFAULT 100,
            daily_rate REAL DEFAULT 10000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Tent profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tent_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            tent_types TEXT,
            daily_rate REAL DEFAULT 8000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Caterer profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caterer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            menu_types TEXT,
            daily_rate REAL DEFAULT 7000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()

    # Get all users and create their role profiles
    cursor.execute("SELECT id, username, role FROM users WHERE role != 'client'")
    users = cursor.fetchall()

    profile_created = 0
    for user in users:
        user_id = user[0]
        username = user[1]
        role = user[2]

        try:
            if role == 'dj':
                cursor.execute('''
                    INSERT OR IGNORE INTO dj_equipment (user_id, equipment, total_per_event)
                    VALUES (?, ?, 5000.0)
                ''', (user_id, 'Pioneer DDJ-400, Laptop, JBL Speakers'))
                profile_created += cursor.rowcount
            elif role == 'photographer':
                cursor.execute('''
                    INSERT OR IGNORE INTO photographer_profiles (user_id, specialization, daily_rate)
                    VALUES (?, 'Event Photography', 3000.0)
                ''', (user_id,))
                profile_created += cursor.rowcount
            elif role == 'venue':
                cursor.execute('''
                    INSERT OR IGNORE INTO venue_profiles (user_id, capacity, daily_rate)
                    VALUES (?, 100, 10000.0)
                ''', (user_id,))
                profile_created += cursor.rowcount
            elif role == 'tent':
                cursor.execute('''
                    INSERT OR IGNORE INTO tent_profiles (user_id, tent_types, daily_rate)
                    VALUES (?, 'Marquee, Gazebo, Dome', 8000.0)
                ''', (user_id,))
                profile_created += cursor.rowcount
            elif role == 'caterer':
                cursor.execute('''
                    INSERT OR IGNORE INTO caterer_profiles (user_id, menu_types, daily_rate)
                    VALUES (?, 'Buffet, Plated, Cocktail', 7000.0)
                ''', (user_id,))
                profile_created += cursor.rowcount
        except Exception:
            pass

    conn.commit()
    conn.close()
    print(f"  {profile_created} role-specific profiles created")


def sync_to_booking_db():
    """Sync users from curyent.db to booking.db."""
    print("\nSyncing users to booking.db...")
    curyent_conn = sqlite3.connect(curyent_db)
    curyent_cursor = curyent_conn.cursor()
    curyent_cursor.execute("SELECT * FROM users")
    users = curyent_cursor.fetchall()
    curyent_conn.close()

    booking_conn = sqlite3.connect(booking_db)
    booking_cursor = booking_conn.cursor()
    booking_cursor.execute('''
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

    synced = 0
    for user in users:
        booking_cursor.execute('''
            INSERT OR REPLACE INTO users (id, username, email, password, role, title, phone, location, profile_image, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', user)
        synced += 1

    booking_conn.commit()
    booking_conn.close()
    print(f"  {synced} users synced to booking.db")


def sync_to_social_db():
    """Sync users from curyent.db to social.db."""
    print("\nSyncing users to social.db...")
    curyent_conn = sqlite3.connect(curyent_db)
    curyent_cursor = curyent_conn.cursor()
    curyent_cursor.execute("SELECT * FROM users")
    users = curyent_cursor.fetchall()
    curyent_conn.close()

    social_conn = sqlite3.connect(social_db)
    social_cursor = social_conn.cursor()
    social_cursor.execute('''
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

    synced = 0
    for user in users:
        social_cursor.execute('''
            INSERT OR REPLACE INTO users (id, username, email, password, role, title, phone, location, profile_image, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', user)
        synced += 1

    social_conn.commit()
    social_conn.close()
    print(f"  {synced} users synced to social.db")


def main():
    print("=" * 60)
    print("CREATING 120 SAMPLE USERS FOR CURYENT DEMO")
    print("=" * 60)
    print(f"Password for all users: {PASSWORD}")
    print()

    # Create users in curyent.db
    create_users_in_db(curyent_db, 'curyent.db')

    # Sync to booking.db
    sync_to_booking_db()

    # Sync to probase.db and create role profiles
    create_users_in_db(probase_db, 'probase.db')
    create_role_profiles()

    # Sync to social.db
    sync_to_social_db()

    print()
    print("=" * 60)
    print("SAMPLE USERS CREATED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("User counts per role:")
    print(f"  Clients:       20 (alex, sarah, mike, emma, ...)")
    print(f"  DJs:           20 (dj_beats, dj_mixmaster, dj_spinmaster, ...)")
    print(f"  Photographers: 20 (photo_lens, photo_shutter, photo_capture, ...)")
    print(f"  Venues:        20 (mark_hotel, olives_garden, sunset_resort, ...)")
    print(f"  Tents:         20 (royal_marquee, elegant_canopy, grand_tent_co, ...)")
    print(f"  Caterers:      20 (delight_catering, flavor_kitchen, taste_bites, ...)")
    print()
    print(f"All users share the password: {PASSWORD}")
    print()
    print("Reload your web app on PythonAnywhere to see the users.")
    print("=" * 60)


if __name__ == '__main__':
    main()
