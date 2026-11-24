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
from werkzeug.security import generate_password_hash

# Database paths
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')
social_db = os.path.join(base_dir, 'social.db')

PASSWORD = 'curyent2024'
HASHED_PASSWORD = generate_password_hash(PASSWORD)

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

# Caterers — realistic Kenyan catering business names (chef-led, personal kitchens)
cater_names = [
    'Lilies Kitchen', 'Chef Oliye', 'Mama Olie’s Kitchen', 'Chef Kamau Catering',
    'Nyama Choma House', 'Mama Njeri’s Table', 'Chef Baraka Foods',
    'Mama Zawadi Kitchen', 'Chef Amani Catering', 'Mama Wanjiku’s Feast',
    'Chef Juma’s Kitchen', 'Mama Aisha Catering', 'Chef Hassan Foods',
    'Mama Akinyi’s Table', 'Chef Peter’s Kitchen', 'Mama Grace Catering',
    'Chef Brian’s Feast', 'Mama Faith Kitchen', 'Chef David Catering',
    'Mama Rose’s Kitchen'
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
    updated = 0

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
            ''', (username, email, HASHED_PASSWORD, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
                # Update existing user's password to hashed version
                cursor.execute('''
                    UPDATE users SET password = ? WHERE username = ?
                ''', (HASHED_PASSWORD, username))
                if cursor.rowcount > 0:
                    updated += 1
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
            ''', (username, email, HASHED_PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
                # Update existing user's password to hashed version
                cursor.execute('''
                    UPDATE users SET password = ? WHERE username = ?
                ''', (HASHED_PASSWORD, username))
                if cursor.rowcount > 0:
                    updated += 1
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
            ''', (username, email, HASHED_PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
                # Update existing user's password to hashed version
                cursor.execute('''
                    UPDATE users SET password = ? WHERE username = ?
                ''', (HASHED_PASSWORD, username))
                if cursor.rowcount > 0:
                    updated += 1
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
            ''', (username, email, HASHED_PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
                # Update existing user's password to hashed version
                cursor.execute('''
                    UPDATE users SET password = ? WHERE username = ?
                ''', (HASHED_PASSWORD, username))
                if cursor.rowcount > 0:
                    updated += 1
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
            ''', (username, email, HASHED_PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
                # Update existing user's password to hashed version
                cursor.execute('''
                    UPDATE users SET password = ? WHERE username = ?
                ''', (HASHED_PASSWORD, username))
                if cursor.rowcount > 0:
                    updated += 1
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
            ''', (username, email, HASHED_PASSWORD, title, phone, location))
            if cursor.rowcount > 0:
                created += 1
            else:
                skipped += 1
                # Update existing user's password to hashed version
                cursor.execute('''
                    UPDATE users SET password = ? WHERE username = ?
                ''', (HASHED_PASSWORD, username))
                if cursor.rowcount > 0:
                    updated += 1
        except Exception:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"  {db_name}: {created} created, {skipped} skipped, {updated} password(s) updated")
    return created


def create_role_profiles():
    """Create role-specific profiles in probase.db with unique rates and details."""
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

    # Unique DJ equipment and rates (varied by experience level)
    dj_equipment_list = [
        ('Pioneer DDJ-1000, CDJ-3000, Allen & Heath Mixer, QSC Speakers', 15000.0),
        ('Pioneer DDJ-FLX4, Laptop, Yamaha Speakers', 8000.0),
        ('Technics SL-1200, Rane Mixer, ELAC Speakers', 12000.0),
        ('Pioneer DDJ-400, Laptop, JBL EON 710', 6000.0),
        ('CDJ-2000NXS2, DJM-900NXS2, Funktion-One Speakers', 18000.0),
        ('Pioneer DDJ-REV7, Rane SL3, QSC K12.2', 10000.0),
        ('Numark Mixtrack Pro FX, Edifier Speakers', 4500.0),
        ('Pioneer DDJ-FLX10, DJM-V10, Funktion-One', 20000.0),
        ('Hercules DJControl Inpulse 500, Logitech Speakers', 3500.0),
        ('Pioneer CDJ-3000, DJM-V10, L-Acoustics', 25000.0),
        ('Vestax VCI-400, Laptop, Bose Speakers', 5500.0),
        ('Pioneer DDJ-1000Saber, DJM-900NXS2, QSC', 14000.0),
        ('Native Instruments S4, Traktor Kontrol S4, Edifier', 4000.0),
        ('Pioneer DDJ-FLX4, Mackie Thump Speakers', 7000.0),
        ('Technics SL-1210, Reloop Mixer, ELAC Debut', 11000.0),
        ('Pioneer DDJ-ATM1, Laptop, JBL PartyBox', 5000.0),
        ('CDJ-2000, DJM-900, Funktion-One Cobalt', 16000.0),
        ('Pioneer DDJ-400, Edifier R1280T', 3000.0),
        ('Pioneer DDJ-REV7, Rane SL3, QSC K12.2', 9500.0),
        ('Pioneer XDJ-RX2, RCF Speakers', 13000.0),
    ]

    # Unique photographer specializations and rates
    photo_specializations = [
        ('Wedding & Portrait Photography', 5000.0),
        ('Event & Corporate Photography', 4000.0),
        ('Wedding & Documentary Photography', 6000.0),
        ('Portrait & Fashion Photography', 3500.0),
        ('Event & Concert Photography', 4500.0),
        ('Wedding & Lifestyle Photography', 5500.0),
        ('Product & Commercial Photography', 7000.0),
        ('Event & Social Photography', 3000.0),
        ('Wedding & Fine Art Photography', 8000.0),
        ('Sports & Action Photography', 4000.0),
        ('Portrait & Headshot Photography', 2500.0),
        ('Event & Nightlife Photography', 3500.0),
        ('Wedding & Engagement Photography', 5000.0),
        ('Food & Culinary Photography', 6500.0),
        ('Aerial & Drone Photography', 9000.0),
        ('Event & Festival Photography', 3000.0),
        ('Wedding & Traditional Photography', 4500.0),
        ('Architecture & Interior Photography', 7500.0),
        ('Event & Birthday Photography', 2000.0),
        ('Wedding & Luxury Photography', 10000.0),
    ]

    # Unique venue capacities and rates
    venue_details = [
        (500, 25000.0),   # Mark Hotel - large
        (150, 12000.0),   # Olives Garden - medium
        (300, 20000.0),   # Sunset Resort - large
        (200, 15000.0),   # Royal Lodge - medium
        (400, 30000.0),   # Grand Ballroom - very large
        (100, 8000.0),    # Emerald Gardens - small
        (350, 22000.0),   # Skyline Hotel - large
        (250, 18000.0),   # Lakeside Resort - medium-large
        (180, 14000.0),   # Palm Beach Hotel - medium
        (120, 10000.0),   # Heritage Lodge - small-medium
        (600, 35000.0),   # Crystal Hall - very large
        (80, 6000.0),     # Golden Acres - small
        (200, 16000.0),   # Sunrise Garden - medium
        (450, 28000.0),   # The Grand Pavilion - very large
        (280, 19000.0),   # Olive Tree Resort - medium-large
        (150, 11000.0),   # Marigold Hotel - medium
        (100, 9000.0),    # Savanna Lodge - small
        (320, 21000.0),   # Blue Waters Resort - large
        (90, 7000.0),     # Crown Gardens - small
        (500, 32000.0),   # Elegance Hall - very large
    ]

    # Unique tent types and rates
    tent_details = [
        ('Royal Marquee (500 guests), VIP Lounge Setup', 20000.0),
        ('Gazebo (100 guests), Garden Party Setup', 8000.0),
        ('Grand Marquee (300 guests), Full Lighting', 15000.0),
        ('Celestial Dome (200 guests), Starlight Effect', 18000.0),
        ('Prestige Marquee (250 guests), Sound System', 12000.0),
        ('Golden Marquee (400 guests), Premium Decor', 25000.0),
        ('Luxury Canopy (150 guests), Air Conditioning', 14000.0),
        ('Crystal Clear Dome (100 guests), Panoramic View', 22000.0),
        ('Sunrise Marquee (200 guests), Open Side Design', 10000.0),
        ('Emerald Pavilion (300 guests), Garden Theme', 16000.0),
        ('Skyline Marquee (350 guests), Rooftop Setup', 19000.0),
        ('Heritage Marquee (180 guests), Traditional Design', 11000.0),
        ('Olive Branch Canopy (120 guests), Rustic Style', 9000.0),
        ('Savanna Marquee (250 guests), Open Air', 13000.0),
        ('Blue Sky Dome (150 guests), Transparent Roof', 21000.0),
        ('Crown Marquee (400 guests), Royal Theme', 24000.0),
        ('Golden Gate Marquee (200 guests), Entrance Arch', 12000.0),
        ('Sunset Canopy (100 guests), Beach Setup', 7000.0),
        ('Pearl Pavilion (280 guests), Elegant Draping', 17000.0),
        ('Diamond Marquee (500 guests), Full Service', 30000.0),
    ]

    # Unique caterer menu types and rates
    caterer_details = [
        ('Kenyan Traditional, Nyama Choma, Ugali & Sukuma', 5000.0),
        ('Continental, Grilled Meats, Seafood Platter', 12000.0),
        ('Home Cooking, Kenyan Fusion, Family Style', 4000.0),
        ('Professional Catering, Buffet & Plated Service', 15000.0),
        ('BBQ Specialist, Grilled Meats, Sides & Sauces', 8000.0),
        ('Traditional Kenyan, Chapati, Samosas, Stews', 3500.0),
        ('International Cuisine, Multi-Course Meals', 18000.0),
        ('Home-Style Cooking, Comfort Food, Desserts', 4500.0),
        ('Corporate Catering, Boxed Lunches, Buffets', 10000.0),
        ('Traditional Feasts, Roasted Whole Goat, Rice', 6000.0),
        ('Chef-Prepared, Fusion Cuisine, Custom Menus', 14000.0),
        ('Halal Catering, Middle Eastern, Kenyan Blend', 7000.0),
        ('Asian-Kenyan Fusion, Noodles, Rice, Curries', 9000.0),
        ('Traditional Breakfast, Brunch, Afternoon Tea', 5500.0),
        ('Gourmet Catering, Fine Dining, Wine Pairing', 20000.0),
        ('Home Baking, Cakes, Pastries, Light Meals', 3000.0),
        ('Wedding Catering, Full Service, Decor Included', 16000.0),
        ('Street Food Style, Kibuyu, Mandazi, Beverages', 2500.0),
        ('Vegetarian & Vegan Options, Healthy Meals', 8500.0),
        ('Family Kitchen, Traditional Recipes, Large Quantities', 4000.0),
    ]

    # Get all users and create their role profiles
    cursor.execute("SELECT id, username, role FROM users WHERE role != 'client'")
    users = cursor.fetchall()

    profile_created = 0
    dj_index = 0
    photo_index = 0
    venue_index = 0
    tent_index = 0
    caterer_index = 0

    for user in users:
        user_id = user[0]
        username = user[1]
        role = user[2]

        try:
            if role == 'dj':
                equipment, rate = dj_equipment_list[dj_index % len(dj_equipment_list)]
                cursor.execute('''
                    INSERT OR IGNORE INTO dj_equipment (user_id, equipment, total_per_event)
                    VALUES (?, ?, ?)
                ''', (user_id, equipment, rate))
                profile_created += cursor.rowcount
                dj_index += 1
            elif role == 'photographer':
                spec, rate = photo_specializations[photo_index % len(photo_specializations)]
                cursor.execute('''
                    INSERT OR IGNORE INTO photographer_profiles (user_id, specialization, daily_rate)
                    VALUES (?, ?, ?)
                ''', (user_id, spec, rate))
                profile_created += cursor.rowcount
                photo_index += 1
            elif role == 'venue':
                capacity, rate = venue_details[venue_index % len(venue_details)]
                cursor.execute('''
                    INSERT OR IGNORE INTO venue_profiles (user_id, capacity, daily_rate)
                    VALUES (?, ?, ?)
                ''', (user_id, capacity, rate))
                profile_created += cursor.rowcount
                venue_index += 1
            elif role == 'tent':
                tent_types, rate = tent_details[tent_index % len(tent_details)]
                cursor.execute('''
                    INSERT OR IGNORE INTO tent_profiles (user_id, tent_types, daily_rate)
                    VALUES (?, ?, ?)
                ''', (user_id, tent_types, rate))
                profile_created += cursor.rowcount
                tent_index += 1
            elif role == 'caterer':
                menu_types, rate = caterer_details[caterer_index % len(caterer_details)]
                cursor.execute('''
                    INSERT OR IGNORE INTO caterer_profiles (user_id, menu_types, daily_rate)
                    VALUES (?, ?, ?)
                ''', (user_id, menu_types, rate))
                profile_created += cursor.rowcount
                caterer_index += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    print(f"  {profile_created} role-specific profiles created with unique rates")


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
    print(f"  Caterers:      20 (lilies_kitchen, chef_oliye, mama_olies_kitchen, ...)")
    print()
    print(f"All users share the password: {PASSWORD}")
    print()
    print("Reload your web app on PythonAnywhere to see the users.")
    print("=" * 60)


if __name__ == '__main__':
    main()
