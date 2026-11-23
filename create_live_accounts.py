"""
One-time script to create test accounts on the live PythonAnywhere server.
Run this in the PythonAnywhere Bash console:
    cd /home/dijayberry/curyent
    python create_live_accounts.py
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database paths (relative to project root on PythonAnywhere)
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')

def create_accounts():
    print("=" * 60)
    print("CREATING TEST ACCOUNTS ON LIVE SERVER")
    print("=" * 60)
    print()

    # 1. Create accounts in curyent.db
    conn = sqlite3.connect(curyent_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if testclient exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('testclient',))
    client_row = cursor.fetchone()

    if client_row:
        client_id = client_row['id']
        print(f"testclient already exists (ID: {client_id}), updating password...")
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (generate_password_hash('client123'), 'testclient')
        )
    else:
        cursor.execute(
            'INSERT INTO users (username, email, password, role, title, phone, location, profile_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('testclient', 'client@curyent.test', generate_password_hash('client123'), 'client', '', '+254712345678', 'Nairobi', None)
        )
        client_id = cursor.lastrowid
        print(f"Created testclient (ID: {client_id})")

    # Check if testdj exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('testdj',))
    dj_row = cursor.fetchone()

    if dj_row:
        dj_id = dj_row['id']
        print(f"testdj already exists (ID: {dj_id}), updating password...")
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (generate_password_hash('dj123'), 'testdj')
        )
    else:
        cursor.execute(
            'INSERT INTO users (username, email, password, role, title, phone, location, profile_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('testdj', 'dj@curyent.test', generate_password_hash('dj123'), 'dj', 'Professional DJ', '+254798765432', 'Nairobi', None)
        )
        dj_id = cursor.lastrowid
        print(f"Created testdj (ID: {dj_id})")

    # Insert DJ equipment for testdj
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dj_equipment'")
    if cursor.fetchone():
        cursor.execute("SELECT id FROM dj_equipment WHERE user_id = ?", (dj_id,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO dj_equipment (user_id, pc_model, controller_model, mixer_model, speakers_model, speakers_quantity, total_per_event) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (dj_id, 'Laptop PC', 'Pioneer DDJ-400', 'Pioneer DJM-250MK2', 'JBL EON 710', 2, 5000)
            )
            print("Added DJ equipment for testdj")
        else:
            print("DJ equipment already exists for testdj")

    conn.commit()
    conn.close()
    print()

    # 2. Sync users to booking.db
    print("Syncing users to booking.db...")
    conn = sqlite3.connect(booking_db)
    cursor = conn.cursor()

    # Create users table in booking.db if it doesn't exist
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

    # Insert or update test accounts
    for username, email, password, role, title, phone, location in [
        ('testclient', 'client@curyent.test', generate_password_hash('client123'), 'client', '', '+254712345678', 'Nairobi'),
        ('testdj', 'dj@curyent.test', generate_password_hash('dj123'), 'dj', 'Professional DJ', '+254798765432', 'Nairobi')
    ]:
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
    print("Synced to booking.db")

    # 3. Sync users to probase.db
    print("Syncing users to probase.db...")
    conn = sqlite3.connect(probase_db)
    cursor = conn.cursor()

    # Create users table in probase.db if it doesn't exist
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

    # Insert or update test accounts
    for username, email, password, role, title, phone, location in [
        ('testclient', 'client@curyent.test', generate_password_hash('client123'), 'client', '', '+254712345678', 'Nairobi'),
        ('testdj', 'dj@curyent.test', generate_password_hash('dj123'), 'dj', 'Professional DJ', '+254798765432', 'Nairobi')
    ]:
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
    print("Synced to probase.db")

    print()
    print("=" * 60)
    print("ACCOUNTS CREATED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Account 1 — CLIENT:")
    print("  Username: testclient")
    print("  Password: client123")
    print("  Role: client")
    print("  Phone: +254712345678")
    print("  Location: Nairobi")
    print()
    print("Account 2 — DJ:")
    print("  Username: testdj")
    print("  Password: dj123")
    print("  Role: dj")
    print("  Title: Professional DJ")
    print("  Phone: +254798765432")
    print("  Location: Nairobi")
    print("  Equipment: Pioneer DDJ-400, Laptop PC, JBL EON 710")
    print()
    print("Login at: https://dijayberry.pythonanywhere.com/login")
    print("=" * 60)


if __name__ == '__main__':
    create_accounts()
