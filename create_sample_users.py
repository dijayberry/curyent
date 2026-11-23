"""
One-time script to create 120 sample users on the live PythonAnywhere server.
20 users per role: client, dj, photographer, venue, tent, caterer.
All users share the same password for easy testing.

Run this in the PythonAnywhere Bash console:
    cd /home/dijayberry/curyent
    python create_sample_users.py
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database paths
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')

PASSWORD = 'curyent2024'
HASHED_PASSWORD = generate_password_hash(PASSWORD)

# =========================
# Sample user data: 20 per role
# =========================

clients = [
    ('client_alex', 'alex@curyent.test', 'Alex Mwangi', '+254711001001', 'Nairobi'),
    ('client_sarah', 'sarah@curyent.test', 'Sarah Ochieng', '+254711001002', 'Mombasa'),
    ('client_james', 'james@curyent.test', 'James Kipchoge', '+254711001003', 'Nakuru'),
    ('client_grace', 'grace@curyent.test', 'Grace Wanjiku', '+254711001004', 'Kisumu'),
    ('client_david', 'david@curyent.test', 'David Omondi', '+254711001005', 'Eldoret'),
    ('client_mary', 'mary@curyent.test', 'Mary Akinyi', '+254711001006', 'Thika'),
    ('client_peter', 'peter@curyent.test', 'Peter Kamau', '+254711001007', 'Nyeri'),
    ('client_linda', 'linda@curyent.test', 'Linda Chebet', '+254711001008', 'Kangundo'),
    ('client_john', 'john@curyent.test', 'John Mutua', '+254711001009', 'Malindi'),
    ('client_fatima', 'fatima@curyent.test', 'Fatima Hassan', '+254711001010', 'Garissa'),
    ('client_brian', 'brian@curyent.test', 'Brian Otieno', '+254711001011', 'Kakamega'),
    ('client_nancy', 'nancy@curyent.test', 'Nancy Wambui', '+254711001012', 'Bungoma'),
    ('client_kevin', 'kevin@curyent.test', 'Kevin Simiyu', '+254711001013', 'Embu'),
    ('client_amina', 'amina@curyent.test', 'Amina Mohamed', '+254711001014', 'Machakos'),
    ('client_steven', 'steven@curyent.test', 'Steven Korir', '+254711001015', 'Kiambu'),
    ('client_jane', 'jane@curyent.test', 'Jane Nyambura', '+254711001016', 'Uasin Gishu'),
    ('client_michael', 'michael@curyent.test', 'Michael Gathuru', '+254711001017', 'Trans Nzoia'),
    ('client_helen', 'helen@curyent.test', 'Helen Adhiambo', '+254711001018', 'Vihiga'),
    ('client_robert', 'robert@curyent.test', 'Robert Njoroge', '+254711001019', 'Meru'),
    ('client_clara', 'clara@curyent.test', 'Clara Wairimu', '+254711001020', 'Nairobi'),
]

djs = [
    ('dj_beats', 'dj.beats@curyent.test', 'DJ Beats', 'Professional Event DJ', '+254722001001', 'Nairobi', 5000),
    ('dj_spin', 'dj.spin@curyent.test', 'DJ Spin', 'Wedding & Party DJ', '+254722001002', 'Mombasa', 4500),
    ('dj_vibes', 'dj.vibes@curyent.test', 'DJ Vibes', 'Club & Festival DJ', '+254722001003', 'Nakuru', 6000),
    ('dj_flash', 'dj.flash@curyent.test', 'DJ Flash', 'Mobile DJ Services', '+254722001004', 'Kisumu', 4000),
    ('dj_melo', 'dj.melo@curyent.test', 'DJ Melo', 'Afrobeat Specialist', '+254722001005', 'Eldoret', 5500),
    ('dj_rhythm', 'dj.rhythm@curyent.test', 'DJ Rhythm', 'Corporate Events DJ', '+254722001006', 'Thika', 7000),
    ('dj_soul', 'dj.soul@curyent.test', 'DJ Soul', 'Soul & R&B DJ', '+254722001007', 'Nyeri', 4800),
    ('dj_bass', 'dj.bass@curyent.test', 'DJ Bass', 'Hip Hop & Dancehall', '+254722001008', 'Kangundo', 5200),
    ('dj_echo', 'dj.echo@curyent.test', 'DJ Echo', 'Birthday Party DJ', '+254722001009', 'Malindi', 3500),
    ('dj_pulse', 'dj.pulse@curyent.test', 'DJ Pulse', 'Gospel & Church DJ', '+254722001010', 'Garissa', 4200),
    ('dj_wave', 'dj.wave@curyent.test', 'DJ Wave', 'House & Techno DJ', '+254722001011', 'Kakamega', 5800),
    ('dj_fusion', 'dj.fusion@curyent.test', 'DJ Fusion', 'Multi-Genre DJ', '+254722001012', 'Bungoma', 5000),
    ('dj_nova', 'dj.nova@curyent.test', 'DJ Nova', 'Graduation DJ', '+254722001013', 'Embu', 4600),
    ('dj_storm', 'dj.storm@curyent.test', 'DJ Storm', 'Outdoor Events DJ', '+254722001014', 'Machakos', 5300),
    ('dj_zen', 'dj.zen@curyent.test', 'DJ Zen', 'Chill & Lounge DJ', '+254722001015', 'Kiambu', 6500),
    ('dj_blaze', 'dj.blaze@curyent.test', 'DJ Blaze', 'Fire Starter DJ', '+254722001016', 'Uasin Gishu', 4900),
    ('dj_crown', 'dj.crown@curyent.test', 'DJ Crown', 'Royal Events DJ', '+254722001017', 'Trans Nzoia', 7500),
    ('dj_mystic', 'dj.mystic@curyent.test', 'DJ Mystic', 'Mystical Beats DJ', '+254722001018', 'Vihiga', 5100),
    ('dj_prime', 'dj.prime@curyent.test', 'DJ Prime', 'Premium DJ Services', '+254722001019', 'Meru', 6200),
    ('dj_royal', 'dj.royal@curyent.test', 'DJ Royal', 'Luxury Event DJ', '+254722001020', 'Nairobi', 8000),
]

photographers = [
    ('photo_lens', 'photo.lens@curyent.test', 'Lens Photography', 'Wedding Photography', '+254733001001', 'Nairobi', 3000),
    ('photo_snap', 'photo.snap@curyent.test', 'Snap Studio', 'Event Photography', '+254733001002', 'Mombasa', 2800),
    ('photo_focus', 'photo.focus@curyent.test', 'Focus Images', 'Portrait Photography', '+254733001003', 'Nakuru', 3500),
    ('photo_click', 'photo.click@curyent.test', 'Click Moments', 'Corporate Photography', '+254733001004', 'Kisumu', 3200),
    ('photo_vista', 'photo.vista@curyent.test', 'Vista Photos', 'Landscape Photography', '+254733001005', 'Eldoret', 2500),
    ('photo_art', 'photo.art@curyent.test', 'Art Frame Studio', 'Creative Photography', '+254733001006', 'Thika', 4000),
    ('photo_gold', 'photo.gold@curyent.test', 'Golden Lens', 'Luxury Photography', '+254733001007', 'Nyeri', 4500),
    ('photo_star', 'photo.star@curyent.test', 'Star Capture', 'Celebrity Photography', '+254733001008', 'Kangundo', 3800),
    ('photo_dream', 'photo.dream@curyent.test', 'Dream Shots', 'Dream Events Photo', '+254733001009', 'Malindi', 2900),
    ('photo_aura', 'photo.aura@curyent.test', 'Aura Photography', 'Fashion Photography', '+254733001010', 'Garissa', 3300),
    ('photo_pixel', 'photo.pixel@curyent.test', 'Pixel Perfect', 'Product Photography', '+254733001011', 'Kakamega', 3100),
    ('photo_shutter', 'photo.shutter@curyent.test', 'Shutter Bug', 'Wildlife Photography', '+254733001012', 'Bungoma', 2700),
    ('photo_prism', 'photo.prism@curyent.test', 'Prism Studio', 'Studio Photography', '+254733001013', 'Embu', 3600),
    ('photo_zenith', 'photo.zenith@curyent.test', 'Zenith Photos', 'Aerial Photography', '+254733001014', 'Machakos', 5000),
    ('photo_iris', 'photo.iris@curyent.test', 'Iris Lens', 'Family Photography', '+254733001015', 'Kiambu', 2600),
    ('photo_nova', 'photo.nova@curyent.test', 'Nova Images', 'Concert Photography', '+254733001016', 'Uasin Gishu', 3400),
    ('photo_luxe', 'photo.luxe@curyent.test', 'Luxe Photography', 'High-End Events', '+254733001017', 'Trans Nzoia', 4200),
    ('photo_moon', 'photo.moon@curyent.test', 'Moonlight Photos', 'Night Photography', '+254733001018', 'Vihiga', 3700),
    ('photo_sky', 'photo.sky@curyent.test', 'Sky View Studio', 'Drone Photography', '+254733001019', 'Meru', 4800),
    ('photo_pearl', 'photo.pearl@curyent.test', 'Pearl Moments', 'Maternity Photography', '+254733001020', 'Nairobi', 3000),
]

venues = [
    ('venue_grand', 'venue.grand@curyent.test', 'Grand Ballroom', 'Luxury Event Hall', '+254744001001', 'Nairobi', 500, 15000),
    ('venue_palm', 'venue.palm@curyent.test', 'Palm Garden', 'Outdoor Garden Venue', '+254744001002', 'Mombasa', 300, 12000),
    ('venue_royal', 'venue.royal@curyent.test', 'Royal Palace', 'Premium Function Center', '+254744001003', 'Nakuru', 400, 18000),
    ('venue_lake', 'venue.lake@curyent.test', 'Lake View Lodge', 'Lakeside Venue', '+254744001004', 'Kisumu', 250, 10000),
    ('venue_sunset', 'venue.sunset@curyent.test', 'Sunset Terrace', 'Rooftop Venue', '+254744001005', 'Eldoret', 200, 8000),
    ('venue_oasis', 'venue.oasis@curyent.test', 'Oasis Resort', 'Resort Venue', '+254744001006', 'Thika', 350, 14000),
    ('venue_crown', 'venue.crown@curyent.test', 'Crown Hall', 'Wedding Palace', '+254744001007', 'Nyeri', 450, 20000),
    ('venue_emerald', 'venue.emerald@curyent.test', 'Emerald Gardens', 'Garden Venue', '+254744001008', 'Kangundo', 280, 11000),
    ('venue_sapphire', 'venue.sapphire@curyent.test', 'Sapphire Lounge', 'Indoor Lounge', '+254744001009', 'Malindi', 150, 7000),
    ('venue_ruby', 'venue.ruby@curyent.test', 'Ruby Events', 'Multi-Purpose Hall', '+254744001010', 'Garissa', 200, 9000),
    ('venue_diamond', 'venue.diamond@curyent.test', 'Diamond Center', 'Premium Center', '+254744001011', 'Kakamega', 380, 16000),
    ('venue_pearl', 'venue.pearl@curyent.test', 'Pearl Beach', 'Beachfront Venue', '+254744001012', 'Bungoma', 220, 9500),
    ('venue_ivory', 'venue.ivory@curyent.test', 'Ivory Tower', 'Skyline Venue', '+254744001013', 'Embu', 180, 7500),
    ('venue_amber', 'venue.amber@curyent.test', 'Amber Hall', 'Classic Function Hall', '+254744001014', 'Machakos', 320, 13000),
    ('venue_opal', 'venue.opal@curyent.test', 'Opal Gardens', 'Rustic Venue', '+254744001015', 'Kiambu', 260, 10500),
    ('venue_jade', 'venue.jade@curyent.test', 'Jade Palace', 'Asian-Themed Venue', '+254744001016', 'Uasin Gishu', 300, 12500),
    ('venue_onyx', 'venue.onyx@curyent.test', 'Onyx Lounge', 'Modern Venue', '+254744001017', 'Trans Nzoia', 170, 6500),
    ('venue_topaz', 'venue.topaz@curyent.test', 'Topaz Events', 'Corporate Venue', '+254744001018', 'Vihiga', 240, 9800),
    ('venue_garnet', 'venue.garnet@curyent.test', 'Garnet Hall', 'Traditional Venue', '+254744001019', 'Meru', 290, 11500),
    ('venue_crystal', 'venue.crystal@curyent.test', 'Crystal Clear', 'Glass Pavilion', '+254744001020', 'Nairobi', 420, 19000),
]

tents = [
    ('tent_elegant', 'tent.elegant@curyent.test', 'Elegant Tents', 'Marquee Tents', '+254755001001', 'Nairobi', 3000),
    ('tent_premium', 'tent.premium@curyent.test', 'Premium Canopies', 'Premium Tents', '+254755001002', 'Mombasa', 2800),
    ('tent_royal', 'tent.royal@curyent.test', 'Royal Tents Co', 'Royal Tents', '+254755001003', 'Nakuru', 3500),
    ('tent_classic', 'tent.classic@curyent.test', 'Classic Shelters', 'Classic Tents', '+254755001004', 'Kisumu', 2500),
    ('tent_modern', 'tent.modern@curyent.test', 'Modern Tents', 'Modern Canopies', '+254755001005', 'Eldoret', 3200),
    ('tent_luxury', 'tent.luxury@curyent.test', 'Luxury Tents', 'Luxury Marquees', '+254755001006', 'Thika', 4000),
    ('tent_garden', 'tent.garden@curyent.test', 'Garden Tents', 'Garden Canopies', '+254755001007', 'Nyeri', 2700),
    ('tent_beach', 'tent.beach@curyent.test', 'Beach Tents', 'Beach Canopies', '+254755001008', 'Kangundo', 2200),
    ('tent_wedding', 'tent.wedding@curyent.test', 'Wedding Tents', 'Wedding Marquees', '+254755001009', 'Malindi', 3800),
    ('tent_party', 'tent.party@curyent.test', 'Party Tents', 'Party Canopies', '+254755001010', 'Garissa', 2000),
    ('tent_corporate', 'tent.corporate@curyent.test', 'Corporate Tents', 'Corporate Marquees', '+254755001011', 'Kakamega', 3300),
    ('tent_festival', 'tent.festival@curyent.test', 'Festival Tents', 'Festival Canopies', '+254755001012', 'Bungoma', 2900),
    ('tent_vip', 'tent.vip@curyent.test', 'VIP Tents', 'VIP Marquees', '+254755001013', 'Embu', 4500),
    ('tent_safari', 'tent.safari@curyent.test', 'Safari Tents', 'Safari Canopies', '+254755001014', 'Machakos', 2600),
    ('tent_gazebo', 'tent.gazebo@curyent.test', 'Gazebo Tents', 'Gazebo Structures', '+254755001015', 'Kiambu', 2400),
    ('tent_clear', 'tent.clear@curyent.test', 'Clear View Tents', 'Clear Span Tents', '+254755001016', 'Uasin Gishu', 3600),
    ('tent_heated', 'tent.heated@curyent.test', 'Heated Tents', 'Climate-Controlled Tents', '+254755001017', 'Trans Nzoia', 4200),
    ('tent_mini', 'tent.mini@curyent.test', 'Mini Tents', 'Small Canopies', '+254755001018', 'Vihiga', 1800),
    ('tent_mega', 'tent.mega@curyent.test', 'Mega Tents', 'Large Marquees', '+254755001019', 'Meru', 5000),
    ('tent_urban', 'tent.urban@curyent.test', 'Urban Tents', 'City Event Tents', '+254755001020', 'Nairobi', 3100),
]

caterers = [
    ('cater_delight', 'cater.delight@curyent.test', 'Delight Catering', 'Kenyan Cuisine', '+254766001001', 'Nairobi', 500, 500),
    ('cater_taste', 'cater.taste@curyent.test', 'Taste Buds', 'Continental Cuisine', '+254766001002', 'Mombasa', 600, 400),
    ('cater_flavor', 'cater.flavor@curyent.test', 'Flavor House', 'Swahili Cuisine', '+254766001003', 'Nakuru', 450, 300),
    ('cater_gourmet', 'cater.gourmet@curyent.test', 'Gourmet Kitchen', 'Fine Dining', '+254766001004', 'Kisumu', 800, 100),
    ('cater_spice', 'cater.spice@curyent.test', 'Spice Garden', 'Indian Cuisine', '+254766001005', 'Eldoret', 550, 350),
    ('cater_grill', 'cater.grill@curyent.test', 'Grill Masters', 'BBQ & Grill', '+254766001006', 'Thika', 700, 200),
    ('cater_fresh', 'cater.fresh@curyent.test', 'Fresh Bites', 'Healthy Catering', '+254766001007', 'Nyeri', 650, 250),
    ('cater_royal', 'cater.royal@curyent.test', 'Royal Feast', 'Royal Catering', '+254766001008', 'Kangundo', 900, 150),
    ('cater_home', 'cater.home@curyent.test', 'Home Style', 'Home-Cooked Meals', '+254766001009', 'Malindi', 400, 600),
    ('cater_exotic', 'cater.exotic@curyent.test', 'Exotic Flavors', 'International Cuisine', '+254766001010', 'Garissa', 750, 180),
    ('cater_banquet', 'cater.banquet@curyent.test', 'Banquet Pro', 'Banquet Services', '+254766001011', 'Kakamega', 680, 220),
    ('cater_buffet', 'cater.buffet@curyent.test', 'Buffet King', 'Buffet Catering', '+254766001012', 'Bungoma', 520, 450),
    ('cater_vegan', 'cater.vegan@curyent.test', 'Vegan Delights', 'Vegan Catering', '+254766001013', 'Embu', 580, 300),
    ('cater_chef', 'cater.chef@curyent.test', 'Chef Special', 'Chef-Prepared Meals', '+254766001014', 'Machakos', 850, 120),
    ('cater_party', 'cater.party@curyent.test', 'Party Platters', 'Party Catering', '+254766001015', 'Kiambu', 480, 500),
    ('cater_wedding', 'cater.wedding@curyent.test', 'Wedding Feast', 'Wedding Catering', '+254766001016', 'Uasin Gishu', 720, 200),
    ('cater_corp', 'cater.corp@curyent.test', 'Corporate Bites', 'Corporate Catering', '+254766001017', 'Trans Nzoia', 600, 350),
    ('cater_snack', 'cater.snack@curyent.test', 'Snack Attack', 'Snacks & Canapes', '+254766001018', 'Vihiga', 350, 800),
    ('cater_dessert', 'cater.dessert@curyent.test', 'Sweet Treats', 'Dessert Catering', '+254766001019', 'Meru', 420, 400),
    ('cater_premium', 'cater.premium@curyent.test', 'Premium Catering', 'All-You-Can-Eat', '+254766001020', 'Nairobi', 950, 100),
]


def create_all_users():
    print("=" * 60)
    print("CREATING 120 SAMPLE USERS")
    print("=" * 60)
    print(f"Password for all users: {PASSWORD}")
    print()

    all_users = []

    # Clients
    for username, email, name, phone, location in clients:
        all_users.append((username, email, HASHED_PASSWORD, 'client', '', phone, location))

    # DJs
    for username, email, name, title, phone, location, rate in djs:
        all_users.append((username, email, HASHED_PASSWORD, 'dj', title, phone, location))

    # Photographers
    for username, email, name, title, phone, location, rate in photographers:
        all_users.append((username, email, HASHED_PASSWORD, 'photographer', title, phone, location))

    # Venues
    for username, email, name, title, phone, location, capacity, rate in venues:
        all_users.append((username, email, HASHED_PASSWORD, 'venue', title, phone, location))

    # Tents
    for username, email, name, title, phone, location, rate in tents:
        all_users.append((username, email, HASHED_PASSWORD, 'tent', title, phone, location))

    # Caterers
    for username, email, name, title, phone, location, rate, max_guests in caterers:
        all_users.append((username, email, HASHED_PASSWORD, 'caterer', title, phone, location))

    # 1. Insert into curyent.db
    print(f"Inserting {len(all_users)} users into curyent.db...")
    conn = sqlite3.connect(curyent_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    inserted_ids = {}
    for username, email, password, role, title, phone, location in all_users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        if existing:
            uid = existing['id']
            cursor.execute(
                "UPDATE users SET password = ?, role = ?, title = ?, phone = ?, location = ? WHERE username = ?",
                (password, role, title, phone, location, username)
            )
        else:
            cursor.execute(
                'INSERT INTO users (username, email, password, role, title, phone, location) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, email, password, role, title, phone, location)
            )
            uid = cursor.lastrowid
        inserted_ids[username] = uid

    # DJ equipment
    for username, email, name, title, phone, location, rate in djs:
        uid = inserted_ids[username]
        cursor.execute("SELECT id FROM dj_equipment WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO dj_equipment (user_id, pc_model, controller_model, mixer_model, speakers_model, speakers_quantity, total_per_event) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (uid, 'Laptop PC', 'Pioneer DDJ-400', 'Pioneer DJM-250MK2', 'JBL EON 710', 2, rate)
            )

    # Photographer profiles
    for username, email, name, title, phone, location, rate in photographers:
        uid = inserted_ids[username]
        cursor.execute("SELECT id FROM photographer_profiles WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO photographer_profiles (user_id, business_name, specialization, experience, camera_equipment, services, daily_rate) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (uid, name, title, 5, 'Canon EOS R5, Sony A7III', 'Events, Portraits', rate)
            )

    # Event venues
    for username, email, name, title, phone, location, capacity, rate in venues:
        uid = inserted_ids[username]
        cursor.execute("SELECT id FROM event_venues WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO event_venues (user_id, venue_name, venue_type, capacity, amenities, daily_rate) VALUES (?, ?, ?, ?, ?, ?)',
                (uid, name, title, capacity, 'Parking, WiFi, Sound System', rate)
            )

    # Tent inventory
    for username, email, name, title, phone, location, rate in tents:
        uid = inserted_ids[username]
        cursor.execute("SELECT id FROM tent_inventory WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO tent_inventory (user_id, business_name, tent_types, tent_sizes, total_tents, daily_rate) VALUES (?, ?, ?, ?, ?, ?)',
                (uid, name, title, 'Small, Medium, Large', 10, rate)
            )

    # Caterer profiles
    for username, email, name, title, phone, location, rate, max_guests in caterers:
        uid = inserted_ids[username]
        cursor.execute("SELECT id FROM caterer_profiles WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO caterer_profiles (user_id, business_name, cuisine_type, per_person_rate, max_guests, min_guests, daily_rate) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (uid, name, title, rate, max_guests, max_guests // 5, rate * 10)
            )

    conn.commit()
    conn.close()
    print(f"Inserted {len(all_users)} users into curyent.db with role-specific profiles.")
    print()

    # 2. Sync to booking.db
    print("Syncing to booking.db...")
    conn = sqlite3.connect(booking_db)
    cursor = conn.cursor()
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
    for username, email, password, role, title, phone, location in all_users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE users SET password = ?, role = ?, title = ?, phone = ?, location = ? WHERE username = ?",
                (password, role, title, phone, location, username)
            )
        else:
            cursor.execute(
                'INSERT INTO users (username, email, password, role, title, phone, location) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, email, password, role, title, phone, location)
            )
    conn.commit()
    conn.close()
    print("Synced to booking.db.")

    # 3. Sync to probase.db
    print("Syncing to probase.db...")
    conn = sqlite3.connect(probase_db)
    cursor = conn.cursor()
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
    for username, email, password, role, title, phone, location in all_users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE users SET password = ?, role = ?, title = ?, phone = ?, location = ? WHERE username = ?",
                (password, role, title, phone, location, username)
            )
        else:
            cursor.execute(
                'INSERT INTO users (username, email, password, role, title, phone, location) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, email, password, role, title, phone, location)
            )
    conn.commit()
    conn.close()
    print("Synced to probase.db.")

    print()
    print("=" * 60)
    print("120 SAMPLE USERS CREATED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print(f"ALL USERS PASSWORD: {PASSWORD}")
    print()
    print("CLIENTS (20):")
    for u in clients[:5]:
        print(f"  Username: {u[0]}, Name: {u[2]}, Location: {u[4]}")
    print(f"  ... and {len(clients)-5} more")
    print()
    print("DJs (20):")
    for u in djs[:5]:
        print(f"  Username: {u[0]}, Title: {u[3]}, Rate: KES {u[6]}")
    print(f"  ... and {len(djs)-5} more")
    print()
    print("PHOTOGRAPHERS (20):")
    for u in photographers[:5]:
        print(f"  Username: {u[0]}, Title: {u[3]}, Rate: KES {u[6]}")
    print(f"  ... and {len(photographers)-5} more")
    print()
    print("VENUES (20):")
    for u in venues[:5]:
        print(f"  Username: {u[0]}, Title: {u[3]}, Capacity: {u[6]}")
    print(f"  ... and {len(venues)-5} more")
    print()
    print("TENTS (20):")
    for u in tents[:5]:
        print(f"  Username: {u[0]}, Title: {u[3]}, Rate: KES {u[6]}")
    print(f"  ... and {len(tents)-5} more")
    print()
    print("CATERERS (20):")
    for u in caterers[:5]:
        print(f"  Username: {u[0]}, Title: {u[3]}, Per Person: KES {u[6]}")
    print(f"  ... and {len(caterers)-5} more")
    print()
    print("Login at: https://dijayberry.pythonanywhere.com/login")
    print("=" * 60)


if __name__ == '__main__':
    create_all_users()
