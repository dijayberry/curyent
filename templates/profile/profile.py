"""
Profile module — user profile page with personal details, ranking, orders, and feedback.
"""
import sqlite3
import os
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for

# Profile database file path (separate from curyent.db and booking.db)
PROBASE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'probase.db')

# Upload folder for profile images and posts
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Import the main db module to read user data
import templates.account.db as main_db
# Import the booking db module to read order data
import templates.book.book as book_module

profile_bp = Blueprint('profile', __name__)


def get_probase_db():
    """Get a connection to the profile database."""
    conn = sqlite3.connect(PROBASE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_probase_db():
    """Delete and recreate the profile database from scratch, clearing all data.
    If the file is locked, drop all tables instead of deleting the file."""
    if os.path.exists(PROBASE_DB_PATH):
        try:
            os.remove(PROBASE_DB_PATH)
        except PermissionError:
            # File is locked — drop all tables to clear data in place
            conn = get_probase_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table['name']}")
            conn.commit()
            conn.close()
    init_probase_db()
    sync_users_to_probase_db()


def sync_users_to_probase_db():
    """Sync the users table from curyent.db into probase.db so JOIN queries work."""
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT * FROM users')
        users = main_cursor.fetchall()
        main_conn.close()

        pro_conn = get_probase_db()
        pro_cursor = pro_conn.cursor()
        pro_cursor.execute('''
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
        # Add missing columns if they don't exist (for existing databases)
        try:
            pro_cursor.execute('ALTER TABLE users ADD COLUMN profile_image TEXT')
            pro_conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            pro_cursor.execute("ALTER TABLE users ADD COLUMN title TEXT DEFAULT ''")
            pro_conn.commit()
        except sqlite3.OperationalError:
            pass

        # Delete existing users and re-insert to keep in sync
        pro_cursor.execute('DELETE FROM users')
        for u in users:
            pro_cursor.execute('''
                INSERT OR REPLACE INTO users (id, username, email, password, role, title, phone, location, profile_image, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (u['id'], u['username'], u['email'], u['password'], u['role'], u['title'], u['phone'], u['location'], u['profile_image'], u['created_at']))
        pro_conn.commit()
        pro_conn.close()
    except Exception:
        pass  # Users table may not exist yet in curyent.db on first run


def init_probase_db():
    """Initialize the profile database tables."""
    conn = get_probase_db()
    cursor = conn.cursor()

    # Feedback table — stores feedback for users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            from_user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (from_user_id) REFERENCES users(id)
        )
    ''')

    # Posts table — stores user photo posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


# Database initialization moved to app startup (curyent.py) to avoid import-time locks
def ensure_probase_initialized():
    """Call this once at app startup to initialize the profile database.
    Do NOT call at import time — it causes database locks with Flask debug mode."""
    init_probase_db()
    sync_users_to_probase_db()


# =========================
# Data Retrieval Helpers
# =========================

def get_user_profile(user_id):
    """Get full profile data for a user from the main database."""
    conn = main_db.get_db()
    cursor = conn.cursor()

    # Get basic user info
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None

    profile = dict(user)

    # Get role-specific profile data
    role = user['role']
    if role == 'dj':
        cursor.execute('SELECT * FROM dj_equipment WHERE user_id = ?', (user_id,))
        role_data = cursor.fetchone()
        if role_data:
            rd = dict(role_data)
            # Rename total_per_event to daily_rate for template compatibility
            if 'total_per_event' in rd and 'daily_rate' not in rd:
                rd['daily_rate'] = rd['total_per_event']
            profile['role_data'] = rd
    elif role == 'event':
        cursor.execute('SELECT * FROM event_venues WHERE user_id = ?', (user_id,))
        role_data = cursor.fetchone()
        if role_data:
            profile['role_data'] = dict(role_data)
    elif role == 'photographer':
        cursor.execute('SELECT * FROM photographer_profiles WHERE user_id = ?', (user_id,))
        role_data = cursor.fetchone()
        if role_data:
            profile['role_data'] = dict(role_data)
    elif role == 'tent':
        cursor.execute('SELECT * FROM tent_inventory WHERE user_id = ?', (user_id,))
        role_data = cursor.fetchone()
        if role_data:
            profile['role_data'] = dict(role_data)
    elif role == 'caterer':
        cursor.execute('SELECT * FROM caterer_profiles WHERE user_id = ?', (user_id,))
        role_data = cursor.fetchone()
        if role_data:
            profile['role_data'] = dict(role_data)

    conn.close()
    return profile


def get_ranking_stats(user_id):
    """
    Get ranking statistics for a user.
    Returns order counts by status from the booking database.
    """
    book_conn = book_module.get_book_db()
    cursor = book_conn.cursor()

    # Orders made BY this user (as booker)
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM bookings
        WHERE booker_id = ?
        GROUP BY status
    ''', (user_id,))
    orders_made = {row['status']: row['count'] for row in cursor.fetchall()}

    # Orders made FOR this user (as booked)
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM bookings
        WHERE booked_id = ?
        GROUP BY status
    ''', (user_id,))
    orders_received = {row['status']: row['count'] for row in cursor.fetchall()}

    # Total earnings (accepted bookings where user is booked)
    cursor.execute('''
        SELECT COALESCE(SUM(daily_rate * 2), 0) as total_earnings
        FROM bookings
        WHERE booked_id = ? AND status = 'accepted'
    ''', (user_id,))
    earnings = cursor.fetchone()['total_earnings']

    # Average rating from feedback
    probase_conn = get_probase_db()
    probase_cursor = probase_conn.cursor()
    probase_cursor.execute('''
        SELECT AVG(rating) as avg_rating, COUNT(*) as total_feedback
        FROM feedback
        WHERE user_id = ?
    ''', (user_id,))
    rating_row = probase_cursor.fetchone()
    avg_rating = rating_row['avg_rating'] if rating_row['avg_rating'] else 0
    total_feedback = rating_row['total_feedback']

    book_conn.close()
    probase_conn.close()

    return {
        'orders_made': orders_made,
        'orders_received': orders_received,
        'total_earnings': earnings,
        'avg_rating': round(avg_rating, 1),
        'total_feedback': total_feedback,
        'total_orders_made': sum(orders_made.values()),
        'total_orders_received': sum(orders_received.values()),
        'completed_orders': orders_received.get('accepted', 0),
        'pending_orders': orders_received.get('pending', 0),
        'declined_orders': orders_received.get('declined', 0)
    }


def get_orders_for_me(user_id):
    """Get all bookings where the user is the booked person."""
    return book_module.get_received_bookings(user_id)


def get_feedback_for_me(user_id):
    """Get all feedback for a user."""
    conn = get_probase_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, u.username as from_username
        FROM feedback f
        JOIN users u ON f.from_user_id = u.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,))
    feedback_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return feedback_list


# =========================
# Posts Helpers
# =========================

def get_posts_for_user(user_id):
    """Get all posts for a user."""
    conn = get_probase_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM posts
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return posts


def add_post(user_id, image_path, caption=''):
    """Add a new post for a user."""
    conn = get_probase_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (user_id, image_path, caption)
        VALUES (?, ?, ?)
    ''', (user_id, image_path, caption))
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return post_id


def delete_post(post_id, user_id):
    """Delete a post if it belongs to the user."""
    conn = get_probase_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def update_user_profile(user_id, data):
    """Update user profile information."""
    conn = main_db.get_db()
    cursor = conn.cursor()

    # Update basic user info
    fields = []
    values = []
    if 'username' in data and data['username']:
        fields.append('username = ?')
        values.append(data['username'])
    if 'email' in data and data['email']:
        fields.append('email = ?')
        values.append(data['email'])
    if 'phone' in data and data['phone']:
        fields.append('phone = ?')
        values.append(data['phone'])
    if 'location' in data and data['location']:
        fields.append('location = ?')
        values.append(data['location'])
    if 'profile_image' in data and data['profile_image']:
        fields.append('profile_image = ?')
        values.append(data['profile_image'])

    if fields:
        values.append(user_id)
        cursor.execute(f'UPDATE users SET {", ".join(fields)} WHERE id = ?', values)

    # Update role-specific data
    user = get_user_profile(user_id)
    if user:
        role = user['role']
        if role == 'dj' and 'daily_rate' in data:
            cursor.execute('UPDATE dj_equipment SET total_per_event = ? WHERE user_id = ?',
                          (float(data['daily_rate']), user_id))
        elif role == 'event' and 'daily_rate' in data:
            cursor.execute('UPDATE event_venues SET daily_rate = ? WHERE user_id = ?',
                          (float(data['daily_rate']), user_id))
        elif role == 'photographer' and 'daily_rate' in data:
            cursor.execute('UPDATE photographer_profiles SET daily_rate = ? WHERE user_id = ?',
                          (float(data['daily_rate']), user_id))
        elif role == 'tent' and 'daily_rate' in data:
            cursor.execute('UPDATE tent_inventory SET daily_rate = ? WHERE user_id = ?',
                          (float(data['daily_rate']), user_id))
        elif role == 'caterer' and 'daily_rate' in data:
            cursor.execute('UPDATE caterer_profiles SET daily_rate = ? WHERE user_id = ?',
                          (float(data['daily_rate']), user_id))

    conn.commit()
    conn.close()
    return True


# =========================
# Routes
# =========================

@profile_bp.route('/profile')
def profile_page():
    """Render the user profile page."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('account.logi'))

    profile = get_user_profile(user_id)
    stats = get_ranking_stats(user_id)
    orders = get_orders_for_me(user_id)
    feedback = get_feedback_for_me(user_id)
    posts = get_posts_for_user(user_id)

    return render_template('profile/profile.html',
                           profile=profile,
                           stats=stats,
                           orders=orders,
                           feedback=feedback,
                           posts=posts,
                           user_id=user_id)


@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    """API: Get current user's profile data."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    profile = get_user_profile(user_id)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found'}), 404

    return jsonify({'success': True, 'profile': profile})


@profile_bp.route('/api/profile/image', methods=['POST'])
def upload_profile_image():
    """API: Upload or update profile image."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    if 'profile_image' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400

    file = request.files['profile_image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if not (file.filename.lower().split('.')[-1] in allowed_extensions):
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400

    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Generate unique filename
    import uuid
    ext = file.filename.lower().split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Delete old profile image if exists
    try:
        conn = main_db.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT profile_image FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row and row['profile_image']:
            old_filename = os.path.basename(row['profile_image'])
            old_path = os.path.join(UPLOAD_FOLDER, old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        conn.close()
    except Exception:
        pass

    # Save new image
    file.save(file_path)
    image_path = f"/static/uploads/{filename}"

    # Update database
    conn = main_db.get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET profile_image = ? WHERE id = ?', (image_path, user_id))
    conn.commit()
    conn.close()

    # Sync to other databases
    try:
        import templates.account.acc as acc_module
        acc_module.sync_all_dbs()
    except Exception:
        pass

    return jsonify({'success': True, 'image_path': image_path})


@profile_bp.route('/api/profile', methods=['PUT'])
def update_profile():
    """API: Update current user's profile."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    update_user_profile(user_id, data)
    return jsonify({'success': True, 'message': 'Profile updated successfully'})


@profile_bp.route('/api/profile/stats', methods=['GET'])
def get_stats():
    """API: Get ranking statistics for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    stats = get_ranking_stats(user_id)
    return jsonify({'success': True, 'stats': stats})


@profile_bp.route('/api/profile/orders', methods=['GET'])
def get_orders():
    """API: Get orders made for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    orders = get_orders_for_me(user_id)
    return jsonify({'success': True, 'orders': orders})


@profile_bp.route('/api/profile/feedback', methods=['GET'])
def get_feedback():
    """API: Get feedback for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    feedback = get_feedback_for_me(user_id)
    return jsonify({'success': True, 'feedback': feedback})


@profile_bp.route('/api/profile/feedback', methods=['POST'])
def add_feedback():
    """API: Add feedback for a user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    target_user_id = data.get('user_id')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not target_user_id or not rating:
        return jsonify({'success': False, 'message': 'User ID and rating are required'}), 400

    if not 1 <= int(rating) <= 5:
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400

    conn = get_probase_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (user_id, from_user_id, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (target_user_id, user_id, int(rating), comment))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Feedback submitted'})


@profile_bp.route('/profile/signout', methods=['POST'])
def sign_out():
    """Sign out — clear session and redirect to login."""
    session.clear()
    return redirect(url_for('account.logi'))


@profile_bp.route('/profile/logout', methods=['POST'])
def log_out():
    """Log out — same as sign out, clears session and redirects."""
    session.clear()
    return redirect(url_for('account.logi'))


# =========================
# Posts Routes
# =========================


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route('/api/profile/posts', methods=['GET'])
def get_posts():
    """API: Get all posts for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    posts = get_posts_for_user(user_id)
    return jsonify({'success': True, 'posts': posts})


@profile_bp.route('/api/profile/posts', methods=['POST'])
def upload_post():
    """API: Upload a new photo post."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Get the uploaded file
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No image selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400

    # Generate unique filename
    import uuid
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{user_id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Get caption from form data
    caption = request.form.get('caption', '')

    # Save to database
    image_path = f"/static/uploads/{filename}"
    post_id = add_post(user_id, image_path, caption)

    return jsonify({'success': True, 'post_id': post_id, 'image_path': image_path})


@profile_bp.route('/api/profile/posts/<int:post_id>', methods=['DELETE'])
def remove_post(post_id):
    """API: Delete a post."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    # Get post before deleting
    conn = get_probase_db()
    cursor = conn.cursor()
    cursor.execute('SELECT image_path FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Post not found'}), 404

    image_path = row['image_path']
    conn.close()

    # Delete from database
    deleted = delete_post(post_id, user_id)

    # Delete file from disk
    if deleted and image_path:
        # Convert relative path to absolute
        filename = os.path.basename(image_path)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify({'success': deleted, 'message': 'Post deleted' if deleted else 'Failed to delete'})
