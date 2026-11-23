"""
One-time script to remove "client_" prefix from client usernames in the database.
This updates all 3 databases: curyent.db, booking.db, probase.db.

Run this in the PythonAnywhere Bash console:
    cd /home/dijayberry/curyent
    python fix_client_usernames.py
"""
import sqlite3
import os

# Database paths
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')


def fix_client_usernames():
    print("=" * 60)
    print("FIXING CLIENT USERNAMES - Removing 'client_' prefix")
    print("=" * 60)
    print()

    # 1. Update curyent.db
    print("Updating curyent.db...")
    conn = sqlite3.connect(curyent_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all client users with "client_" prefix
    cursor.execute("SELECT id, username FROM users WHERE role = 'client' AND username LIKE 'client_%'")
    clients = cursor.fetchall()

    updated_count = 0
    skipped_count = 0

    for client in clients:
        old_username = client['username']
        new_username = old_username.replace('client_', '', 1)
        user_id = client['id']

        # Check if the new username already exists
        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id))
        if cursor.fetchone():
            print(f"  SKIP: {old_username} -> {new_username} (already exists)")
            skipped_count += 1
        else:
            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
            print(f"  Updated: {old_username} -> {new_username}")
            updated_count += 1

    conn.commit()
    conn.close()
    print(f"curyent.db: {updated_count} updated, {skipped_count} skipped")
    print()

    # 2. Update booking.db
    print("Updating booking.db...")
    conn = sqlite3.connect(booking_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users WHERE role = 'client' AND username LIKE 'client_%'")
    clients = cursor.fetchall()

    booking_updated = 0
    booking_skipped = 0

    for client in clients:
        old_username = client['username']
        new_username = old_username.replace('client_', '', 1)
        user_id = client['id']

        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id))
        if cursor.fetchone():
            booking_skipped += 1
        else:
            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
            booking_updated += 1

    conn.commit()
    conn.close()
    print(f"booking.db: {booking_updated} updated, {booking_skipped} skipped")
    print()

    # 3. Update probase.db
    print("Updating probase.db...")
    conn = sqlite3.connect(probase_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users WHERE role = 'client' AND username LIKE 'client_%'")
    clients = cursor.fetchall()

    probase_updated = 0
    probase_skipped = 0

    for client in clients:
        old_username = client['username']
        new_username = old_username.replace('client_', '', 1)
        user_id = client['id']

        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id))
        if cursor.fetchone():
            probase_skipped += 1
        else:
            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
            probase_updated += 1

    conn.commit()
    conn.close()
    print(f"probase.db: {probase_updated} updated, {probase_skipped} skipped")
    print()

    print("=" * 60)
    print("CLIENT USERNAMES FIXED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("All client usernames now display without the 'client_' prefix.")
    print("Example: 'client_alex' is now 'alex'")
    print()
    print("Reload your web app on PythonAnywhere to see the changes.")
    print("=" * 60)


if __name__ == '__main__':
    fix_client_usernames()
