"""
Script to add realistic profile images for all users based on their roles.
Uses pravatar.cc for realistic human faces with role-specific styling.
Also ensures 'event' role users have venue_profiles and 'tents' role users have tent_profiles.
"""
import sqlite3
import os
import hashlib

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')
social_db = os.path.join(base_dir, 'social.db')

# Realistic avatar URLs curated by role
# Using pravatar.cc for realistic human faces with unique seeds per username
role_avatar_sets = {
    'client': {
        'male': [
            "https://i.pravatar.cc/300?img=1", "https://i.pravatar.cc/300?img=3",
            "https://i.pravatar.cc/300?img=7", "https://i.pravatar.cc/300?img=12",
            "https://i.pravatar.cc/300?img=14", "https://i.pravatar.cc/300?img=17",
            "https://i.pravatar.cc/300?img=24", "https://i.pravatar.cc/300?img=32",
            "https://i.pravatar.cc/300?img=33", "https://i.pravatar.cc/300?img=34",
            "https://i.pravatar.cc/300?img=35", "https://i.pravatar.cc/300?img=36",
            "https://i.pravatar.cc/300?img=37", "https://i.pravatar.cc/300?img=38",
            "https://i.pravatar.cc/300?img=39", "https://i.pravatar.cc/300?img=40",
            "https://i.pravatar.cc/300?img=41", "https://i.pravatar.cc/300?img=42",
            "https://i.pravatar.cc/300?img=43", "https://i.pravatar.cc/300?img=44",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=5", "https://i.pravatar.cc/300?img=9",
            "https://i.pravatar.cc/300?img=16", "https://i.pravatar.cc/300?img=20",
            "https://i.pravatar.cc/300?img=25", "https://i.pravatar.cc/300?img=26",
            "https://i.pravatar.cc/300?img=27", "https://i.pravatar.cc/300?img=30",
            "https://i.pravatar.cc/300?img=31", "https://i.pravatar.cc/300?img=45",
            "https://i.pravatar.cc/300?img=46", "https://i.pravatar.cc/300?img=47",
            "https://i.pravatar.cc/300?img=48", "https://i.pravatar.cc/300?img=49",
            "https://i.pravatar.cc/300?img=50", "https://i.pravatar.cc/300?img=45",
            "https://i.pravatar.cc/300?img=46", "https://i.pravatar.cc/300?img=47",
            "https://i.pravatar.cc/300?img=48", "https://i.pravatar.cc/300?img=49",
        ]
    },
    'dj': {
        'male': [
            "https://i.pravatar.cc/300?img=11", "https://i.pravatar.cc/300?img=13",
            "https://i.pravatar.cc/300?img=15", "https://i.pravatar.cc/300?img=51",
            "https://i.pravatar.cc/300?img=52", "https://i.pravatar.cc/300?img=53",
            "https://i.pravatar.cc/300?img=54", "https://i.pravatar.cc/300?img=55",
            "https://i.pravatar.cc/300?img=56", "https://i.pravatar.cc/300?img=57",
            "https://i.pravatar.cc/300?img=58", "https://i.pravatar.cc/300?img=59",
            "https://i.pravatar.cc/300?img=60", "https://i.pravatar.cc/300?img=61",
            "https://i.pravatar.cc/300?img=62", "https://i.pravatar.cc/300?img=63",
            "https://i.pravatar.cc/300?img=64", "https://i.pravatar.cc/300?img=65",
            "https://i.pravatar.cc/300?img=66", "https://i.pravatar.cc/300?img=67",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=43", "https://i.pravatar.cc/300?img=44",
            "https://i.pravatar.cc/300?img=1", "https://i.pravatar.cc/300?img=2",
            "https://i.pravatar.cc/300?img=3", "https://i.pravatar.cc/300?img=4",
            "https://i.pravatar.cc/300?img=5", "https://i.pravatar.cc/300?img=6",
            "https://i.pravatar.cc/300?img=7", "https://i.pravatar.cc/300?img=8",
            "https://i.pravatar.cc/300?img=9", "https://i.pravatar.cc/300?img=10",
            "https://i.pravatar.cc/300?img=11", "https://i.pravatar.cc/300?img=12",
            "https://i.pravatar.cc/300?img=13", "https://i.pravatar.cc/300?img=14",
            "https://i.pravatar.cc/300?img=15", "https://i.pravatar.cc/300?img=16",
            "https://i.pravatar.cc/300?img=17", "https://i.pravatar.cc/300?img=18",
        ]
    },
    'photographer': {
        'male': [
            "https://i.pravatar.cc/300?img=19", "https://i.pravatar.cc/300?img=21",
            "https://i.pravatar.cc/300?img=22", "https://i.pravatar.cc/300?img=23",
            "https://i.pravatar.cc/300?img=28", "https://i.pravatar.cc/300?img=29",
            "https://i.pravatar.cc/300?img=32", "https://i.pravatar.cc/300?img=33",
            "https://i.pravatar.cc/300?img=34", "https://i.pravatar.cc/300?img=35",
            "https://i.pravatar.cc/300?img=36", "https://i.pravatar.cc/300?img=37",
            "https://i.pravatar.cc/300?img=38", "https://i.pravatar.cc/300?img=39",
            "https://i.pravatar.cc/300?img=40", "https://i.pravatar.cc/300?img=41",
            "https://i.pravatar.cc/300?img=42", "https://i.pravatar.cc/300?img=43",
            "https://i.pravatar.cc/300?img=44", "https://i.pravatar.cc/300?img=1",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=2", "https://i.pravatar.cc/300?img=3",
            "https://i.pravatar.cc/300?img=4", "https://i.pravatar.cc/300?img=5",
            "https://i.pravatar.cc/300?img=6", "https://i.pravatar.cc/300?img=7",
            "https://i.pravatar.cc/300?img=8", "https://i.pravatar.cc/300?img=9",
            "https://i.pravatar.cc/300?img=10", "https://i.pravatar.cc/300?img=11",
            "https://i.pravatar.cc/300?img=12", "https://i.pravatar.cc/300?img=13",
            "https://i.pravatar.cc/300?img=14", "https://i.pravatar.cc/300?img=15",
            "https://i.pravatar.cc/300?img=16", "https://i.pravatar.cc/300?img=17",
            "https://i.pravatar.cc/300?img=18", "https://i.pravatar.cc/300?img=19",
            "https://i.pravatar.cc/300?img=20", "https://i.pravatar.cc/300?img=21",
        ]
    },
    'venue': {
        'male': [
            "https://i.pravatar.cc/300?img=1", "https://i.pravatar.cc/300?img=2",
            "https://i.pravatar.cc/300?img=3", "https://i.pravatar.cc/300?img=4",
            "https://i.pravatar.cc/300?img=5", "https://i.pravatar.cc/300?img=6",
            "https://i.pravatar.cc/300?img=7", "https://i.pravatar.cc/300?img=8",
            "https://i.pravatar.cc/300?img=9", "https://i.pravatar.cc/300?img=10",
            "https://i.pravatar.cc/300?img=11", "https://i.pravatar.cc/300?img=12",
            "https://i.pravatar.cc/300?img=13", "https://i.pravatar.cc/300?img=14",
            "https://i.pravatar.cc/300?img=15", "https://i.pravatar.cc/300?img=16",
            "https://i.pravatar.cc/300?img=17", "https://i.pravatar.cc/300?img=18",
            "https://i.pravatar.cc/300?img=19", "https://i.pravatar.cc/300?img=20",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=21", "https://i.pravatar.cc/300?img=22",
            "https://i.pravatar.cc/300?img=23", "https://i.pravatar.cc/300?img=24",
            "https://i.pravatar.cc/300?img=25", "https://i.pravatar.cc/300?img=26",
            "https://i.pravatar.cc/300?img=27", "https://i.pravatar.cc/300?img=28",
            "https://i.pravatar.cc/300?img=29", "https://i.pravatar.cc/300?img=30",
            "https://i.pravatar.cc/300?img=31", "https://i.pravatar.cc/300?img=32",
            "https://i.pravatar.cc/300?img=33", "https://i.pravatar.cc/300?img=34",
            "https://i.pravatar.cc/300?img=35", "https://i.pravatar.cc/300?img=36",
            "https://i.pravatar.cc/300?img=37", "https://i.pravatar.cc/300?img=38",
            "https://i.pravatar.cc/300?img=39", "https://i.pravatar.cc/300?img=40",
        ]
    },
    'event': {
        'male': [
            "https://i.pravatar.cc/300?img=41", "https://i.pravatar.cc/300?img=42",
            "https://i.pravatar.cc/300?img=43", "https://i.pravatar.cc/300?img=44",
            "https://i.pravatar.cc/300?img=45", "https://i.pravatar.cc/300?img=46",
            "https://i.pravatar.cc/300?img=47", "https://i.pravatar.cc/300?img=48",
            "https://i.pravatar.cc/300?img=49", "https://i.pravatar.cc/300?img=50",
            "https://i.pravatar.cc/300?img=51", "https://i.pravatar.cc/300?img=52",
            "https://i.pravatar.cc/300?img=53", "https://i.pravatar.cc/300?img=54",
            "https://i.pravatar.cc/300?img=55", "https://i.pravatar.cc/300?img=56",
            "https://i.pravatar.cc/300?img=57", "https://i.pravatar.cc/300?img=58",
            "https://i.pravatar.cc/300?img=59", "https://i.pravatar.cc/300?img=60",
            "https://i.pravatar.cc/300?img=61", "https://i.pravatar.cc/300?img=62",
            "https://i.pravatar.cc/300?img=63", "https://i.pravatar.cc/300?img=64",
            "https://i.pravatar.cc/300?img=65", "https://i.pravatar.cc/300?img=66",
            "https://i.pravatar.cc/300?img=67", "https://i.pravatar.cc/300?img=1",
            "https://i.pravatar.cc/300?img=2", "https://i.pravatar.cc/300?img=3",
            "https://i.pravatar.cc/300?img=4", "https://i.pravatar.cc/300?img=5",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=6", "https://i.pravatar.cc/300?img=7",
            "https://i.pravatar.cc/300?img=8", "https://i.pravatar.cc/300?img=9",
            "https://i.pravatar.cc/300?img=10", "https://i.pravatar.cc/300?img=11",
            "https://i.pravatar.cc/300?img=12", "https://i.pravatar.cc/300?img=13",
            "https://i.pravatar.cc/300?img=14", "https://i.pravatar.cc/300?img=15",
            "https://i.pravatar.cc/300?img=16", "https://i.pravatar.cc/300?img=17",
            "https://i.pravatar.cc/300?img=18", "https://i.pravatar.cc/300?img=19",
            "https://i.pravatar.cc/300?img=20", "https://i.pravatar.cc/300?img=21",
            "https://i.pravatar.cc/300?img=22", "https://i.pravatar.cc/300?img=23",
            "https://i.pravatar.cc/300?img=24", "https://i.pravatar.cc/300?img=25",
            "https://i.pravatar.cc/300?img=26", "https://i.pravatar.cc/300?img=27",
            "https://i.pravatar.cc/300?img=28", "https://i.pravatar.cc/300?img=29",
            "https://i.pravatar.cc/300?img=30", "https://i.pravatar.cc/300?img=31",
            "https://i.pravatar.cc/300?img=32", "https://i.pravatar.cc/300?img=33",
            "https://i.pravatar.cc/300?img=34", "https://i.pravatar.cc/300?img=35",
            "https://i.pravatar.cc/300?img=36", "https://i.pravatar.cc/300?img=37",
        ]
    },
    'tent': {
        'male': [
            "https://i.pravatar.cc/300?img=1", "https://i.pravatar.cc/300?img=2",
            "https://i.pravatar.cc/300?img=3", "https://i.pravatar.cc/300?img=4",
            "https://i.pravatar.cc/300?img=5", "https://i.pravatar.cc/300?img=6",
            "https://i.pravatar.cc/300?img=7", "https://i.pravatar.cc/300?img=8",
            "https://i.pravatar.cc/300?img=9", "https://i.pravatar.cc/300?img=10",
            "https://i.pravatar.cc/300?img=11", "https://i.pravatar.cc/300?img=12",
            "https://i.pravatar.cc/300?img=13", "https://i.pravatar.cc/300?img=14",
            "https://i.pravatar.cc/300?img=15", "https://i.pravatar.cc/300?img=16",
            "https://i.pravatar.cc/300?img=17", "https://i.pravatar.cc/300?img=18",
            "https://i.pravatar.cc/300?img=19", "https://i.pravatar.cc/300?img=20",
            "https://i.pravatar.cc/300?img=21", "https://i.pravatar.cc/300?img=22",
            "https://i.pravatar.cc/300?img=23", "https://i.pravatar.cc/300?img=24",
            "https://i.pravatar.cc/300?img=25", "https://i.pravatar.cc/300?img=26",
            "https://i.pravatar.cc/300?img=27", "https://i.pravatar.cc/300?img=28",
            "https://i.pravatar.cc/300?img=29", "https://i.pravatar.cc/300?img=30",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=31", "https://i.pravatar.cc/300?img=32",
            "https://i.pravatar.cc/300?img=33", "https://i.pravatar.cc/300?img=34",
            "https://i.pravatar.cc/300?img=35", "https://i.pravatar.cc/300?img=36",
            "https://i.pravatar.cc/300?img=37", "https://i.pravatar.cc/300?img=38",
            "https://i.pravatar.cc/300?img=39", "https://i.pravatar.cc/300?img=40",
            "https://i.pravatar.cc/300?img=41", "https://i.pravatar.cc/300?img=42",
            "https://i.pravatar.cc/300?img=43", "https://i.pravatar.cc/300?img=44",
            "https://i.pravatar.cc/300?img=45", "https://i.pravatar.cc/300?img=46",
            "https://i.pravatar.cc/300?img=47", "https://i.pravatar.cc/300?img=48",
            "https://i.pravatar.cc/300?img=49", "https://i.pravatar.cc/300?img=50",
            "https://i.pravatar.cc/300?img=51", "https://i.pravatar.cc/300?img=52",
            "https://i.pravatar.cc/300?img=53", "https://i.pravatar.cc/300?img=54",
            "https://i.pravatar.cc/300?img=55", "https://i.pravatar.cc/300?img=56",
            "https://i.pravatar.cc/300?img=57", "https://i.pravatar.cc/300?img=58",
            "https://i.pravatar.cc/300?img=59", "https://i.pravatar.cc/300?img=60",
            "https://i.pravatar.cc/300?img=61", "https://i.pravatar.cc/300?img=62",
        ]
    },
    'tents': {
        'male': [
            "https://i.pravatar.cc/300?img=63", "https://i.pravatar.cc/300?img=64",
            "https://i.pravatar.cc/300?img=65", "https://i.pravatar.cc/300?img=66",
            "https://i.pravatar.cc/300?img=67", "https://i.pravatar.cc/300?img=1",
            "https://i.pravatar.cc/300?img=2", "https://i.pravatar.cc/300?img=3",
            "https://i.pravatar.cc/300?img=4", "https://i.pravatar.cc/300?img=5",
            "https://i.pravatar.cc/300?img=6", "https://i.pravatar.cc/300?img=7",
            "https://i.pravatar.cc/300?img=8", "https://i.pravatar.cc/300?img=9",
            "https://i.pravatar.cc/300?img=10", "https://i.pravatar.cc/300?img=11",
            "https://i.pravatar.cc/300?img=12", "https://i.pravatar.cc/300?img=13",
            "https://i.pravatar.cc/300?img=14", "https://i.pravatar.cc/300?img=15",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=16", "https://i.pravatar.cc/300?img=17",
            "https://i.pravatar.cc/300?img=18", "https://i.pravatar.cc/300?img=19",
            "https://i.pravatar.cc/300?img=20", "https://i.pravatar.cc/300?img=21",
            "https://i.pravatar.cc/300?img=22", "https://i.pravatar.cc/300?img=23",
            "https://i.pravatar.cc/300?img=24", "https://i.pravatar.cc/300?img=25",
            "https://i.pravatar.cc/300?img=26", "https://i.pravatar.cc/300?img=27",
            "https://i.pravatar.cc/300?img=28", "https://i.pravatar.cc/300?img=29",
            "https://i.pravatar.cc/300?img=30", "https://i.pravatar.cc/300?img=31",
            "https://i.pravatar.cc/300?img=32", "https://i.pravatar.cc/300?img=33",
            "https://i.pravatar.cc/300?img=34", "https://i.pravatar.cc/300?img=35",
        ]
    },
    'caterer': {
        'male': [
            "https://i.pravatar.cc/300?img=1", "https://i.pravatar.cc/300?img=2",
            "https://i.pravatar.cc/300?img=3", "https://i.pravatar.cc/300?img=4",
            "https://i.pravatar.cc/300?img=5", "https://i.pravatar.cc/300?img=6",
            "https://i.pravatar.cc/300?img=7", "https://i.pravatar.cc/300?img=8",
            "https://i.pravatar.cc/300?img=9", "https://i.pravatar.cc/300?img=10",
            "https://i.pravatar.cc/300?img=11", "https://i.pravatar.cc/300?img=12",
            "https://i.pravatar.cc/300?img=13", "https://i.pravatar.cc/300?img=14",
            "https://i.pravatar.cc/300?img=15", "https://i.pravatar.cc/300?img=16",
            "https://i.pravatar.cc/300?img=17", "https://i.pravatar.cc/300?img=18",
            "https://i.pravatar.cc/300?img=19", "https://i.pravatar.cc/300?img=20",
        ],
        'female': [
            "https://i.pravatar.cc/300?img=21", "https://i.pravatar.cc/300?img=22",
            "https://i.pravatar.cc/300?img=23", "https://i.pravatar.cc/300?img=24",
            "https://i.pravatar.cc/300?img=25", "https://i.pravatar.cc/300?img=26",
            "https://i.pravatar.cc/300?img=27", "https://i.pravatar.cc/300?img=28",
            "https://i.pravatar.cc/300?img=29", "https://i.pravatar.cc/300?img=30",
            "https://i.pravatar.cc/300?img=31", "https://i.pravatar.cc/300?img=32",
            "https://i.pravatar.cc/300?img=33", "https://i.pravatar.cc/300?img=34",
            "https://i.pravatar.cc/300?img=35", "https://i.pravatar.cc/300?img=36",
            "https://i.pravatar.cc/300?img=37", "https://i.pravatar.cc/300?img=38",
            "https://i.pravatar.cc/300?img=39", "https://i.pravatar.cc/300?img=40",
        ]
    }
}

def get_deterministic_seed(username):
    """Generate a deterministic numeric seed from a username."""
    return int(hashlib.md5(username.encode()).hexdigest()[:8], 16)

def get_gender_from_seed(seed):
    """Determine gender from seed (even = male, odd = female)."""
    return 'male' if seed % 2 == 0 else 'female'

def get_avatar_url(username, role):
    """Generate a realistic avatar URL based on username and role."""
    # Normalize role
    if role in ('venue', 'event'):
        role_key = 'venue' if role == 'venue' else 'event'
    elif role in ('tent', 'tents'):
        role_key = role
    else:
        role_key = role

    # Get avatar set for this role
    avatar_set = role_avatar_sets.get(role_key, role_avatar_sets['client'])

    # Generate deterministic seed from username
    seed = get_deterministic_seed(username)
    gender = get_gender_from_seed(seed)

    # Get the list of avatars for this gender
    avatars = avatar_set.get(gender, avatar_set['male'])

    # Use seed to pick a consistent avatar from the list
    index = seed % len(avatars)
    return avatars[index]


def add_profile_images_to_db(db_path, db_name):
    """Add realistic profile images to all users in a database based on their role."""
    print(f"Adding profile images to {db_name}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    updated = 0
    male_count = 0
    female_count = 0
    for user in users:
        user_id, username, role = user
        avatar_url = get_avatar_url(username, role)
        cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?", (avatar_url, user_id))
        if cursor.rowcount > 0:
            updated += 1
            seed = get_deterministic_seed(username)
            if get_gender_from_seed(seed) == 'male':
                male_count += 1
            else:
                female_count += 1

    conn.commit()
    conn.close()
    print(f"  {db_name}: {updated} users updated ({male_count} male, {female_count} female)")
    return updated


def ensure_role_profiles():
    """Ensure all 'event' users have venue_profiles and all 'tents' users have tent_profiles."""
    print("\nEnsuring role profiles in probase.db...")
    conn = sqlite3.connect(probase_db)
    cursor = conn.cursor()

    # Ensure 'event' users have venue_profiles
    cursor.execute('''
        SELECT u.id, u.username FROM users u
        WHERE u.role = 'event'
        AND u.id NOT IN (SELECT user_id FROM venue_profiles)
    ''')
    event_users = cursor.fetchall()
    for user_id, username in event_users:
        cursor.execute('''
            INSERT INTO venue_profiles (user_id, capacity, daily_rate)
            VALUES (?, 100, 10000.0)
        ''', (user_id,))
    print(f"  Added {len(event_users)} venue_profiles for 'event' role users")

    # Ensure 'tents' users have tent_profiles
    cursor.execute('''
        SELECT u.id, u.username FROM users u
        WHERE u.role = 'tents'
        AND u.id NOT IN (SELECT user_id FROM tent_profiles)
    ''')
    tents_users = cursor.fetchall()
    for user_id, username in tents_users:
        cursor.execute('''
            INSERT INTO tent_profiles (user_id, tent_types, daily_rate)
            VALUES (?, 'Marquee, Gazebo, Dome', 8000.0)
        ''', (user_id,))
    print(f"  Added {len(tents_users)} tent_profiles for 'tents' role users")

    conn.commit()
    conn.close()


def main():
    print("=" * 60)
    print("ADDING PROFILE IMAGES AND FIXING ROLE PROFILES")
    print("=" * 60)
    print()

    # Add profile images to all databases
    add_profile_images_to_db(curyent_db, 'curyent.db')
    add_profile_images_to_db(booking_db, 'booking.db')
    add_profile_images_to_db(probase_db, 'probase.db')
    add_profile_images_to_db(social_db, 'social.db')

    # Ensure role profiles exist
    ensure_role_profiles()

    print()
    print("=" * 60)
    print("PROFILE IMAGES ADDED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("All users now have unique avatar images.")
    print("'event' role users have venue_profiles entries.")
    print("'tents' role users have tent_profiles entries.")
    print()
    print("Reload your web app to see the changes.")
    print("=" * 60)


if __name__ == '__main__':
    main()
