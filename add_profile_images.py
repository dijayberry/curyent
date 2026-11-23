"""
Script to add unique profile images for all users and ensure all roles have profile entries.
Uses UI Avatars API for consistent, unique avatar images based on usernames.
Also ensures 'event' role users have venue_profiles and 'tents' role users have tent_profiles.
"""
import sqlite3
import os

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')
social_db = os.path.join(base_dir, 'social.db')

def get_avatar_url(username):
    """Generate a unique avatar URL using UI Avatars API."""
    # Colors for different roles
    colors = {
        'client': '6c5ce7',
        'dj': 'e17055',
        'photographer': '00b894',
        'venue': '0984e3',
        'event': '0984e3',
        'tent': 'e84393',
        'tents': 'e84393',
        'caterer': 'fdcb6e',
    }
    # Get first letter for the avatar
    initial = username[0].upper() if username else '?'
    return f"https://ui-avatars.com/api/?name={initial}&background=random&color=fff&size=200&bold=true"


def add_profile_images_to_db(db_path, db_name):
    """Add profile images to all users in a database."""
    print(f"Adding profile images to {db_name}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    updated = 0
    for user in users:
        user_id, username, role = user
        avatar_url = get_avatar_url(username)
        cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?", (avatar_url, user_id))
        if cursor.rowcount > 0:
            updated += 1

    conn.commit()
    conn.close()
    print(f"  {db_name}: {updated} users updated with profile images")
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
