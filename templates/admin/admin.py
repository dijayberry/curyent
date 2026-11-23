"""
Admin blueprint — management panel for CURYENT.
Provides database browsing, user management, booking management, and UI customization.
"""
import sqlite3
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import templates.admin.admin_db as admin_db
import templates.account.db as main_db
import templates.book.book as book_module
import templates.profile.profile as profile_module
import templates.chat.chat as chat_module
import templates.notifications.noti as noti_module

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# =========================
# Authentication Helper
# =========================

def require_admin(f):
    """Decorator to require admin authentication."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# =========================
# Login / Logout
# =========================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if session.get('admin_authenticated'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        if admin_db.verify_admin_password(password):
            session['admin_authenticated'] = True
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/login.html', error='Incorrect password')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin.login'))


# =========================
# Dashboard
# =========================

@admin_bp.route('/')
@require_admin
def dashboard():
    """Admin dashboard with statistics overview."""
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)


def get_dashboard_stats():
    """Gather statistics from all databases."""
    stats = {}

    # Main DB stats
    try:
        conn = main_db.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        stats['total_users'] = cursor.fetchone()['count']

        cursor.execute('SELECT role, COUNT(*) as count FROM users GROUP BY role')
        stats['users_by_role'] = {row['role']: row['count'] for row in cursor.fetchall()}

        cursor.execute('SELECT COUNT(*) as count FROM dj_equipment')
        stats['total_djs_equipped'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM event_venues')
        stats['total_venues'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM photographer_profiles')
        stats['total_photographers'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM tent_inventory')
        stats['total_tents'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM caterer_profiles')
        stats['total_caterers'] = cursor.fetchone()['count']

        conn.close()
    except Exception:
        pass

    # Booking DB stats
    try:
        conn = book_module.get_book_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM bookings')
        stats['total_bookings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
        stats['pending_bookings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'accepted'")
        stats['accepted_bookings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'declined'")
        stats['declined_bookings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE payout_status = 'paid'")
        stats['paid_bookings'] = cursor.fetchone()['count']

        conn.close()
    except Exception:
        pass

    # Chat DB stats
    try:
        conn = chat_module.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM conversations')
        stats['total_conversations'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM messages')
        stats['total_messages'] = cursor.fetchone()['count']

        conn.close()
    except Exception:
        pass

    # Notification DB stats
    try:
        conn = noti_module.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM notifications')
        stats['total_notifications'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM notifications WHERE is_read = 0')
        stats['unread_notifications'] = cursor.fetchone()['count']

        conn.close()
    except Exception:
        pass

    # Probase DB stats
    try:
        conn = profile_module.get_probase_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM feedback')
        stats['total_feedback'] = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM posts')
        stats['total_posts'] = cursor.fetchone()['count']

        conn.close()
    except Exception:
        pass

    return stats


# =========================
# Database Browser
# =========================

@admin_bp.route('/databases')
@require_admin
def databases():
    """List all databases and their tables."""
    db_info = get_all_db_info()
    return render_template('admin/databases.html', db_info=db_info)


def get_all_db_info():
    """Get information about all databases and their tables."""
    dbs = [
        ('curyent.db', main_db.get_db, main_db.DB_PATH),
        ('booking.db', book_module.get_book_db, book_module.BOOK_DB_PATH),
        ('probase.db', profile_module.get_probase_db, profile_module.PROBASE_DB_PATH),
        ('chatbase.db', chat_module.get_db, chat_module.CHAT_DB_PATH),
        ('notibase.db', noti_module.get_db, noti_module.NOTI_DB_PATH),
        ('admin.db', admin_db.get_db, admin_db.ADMIN_DB_PATH),
    ]

    db_info = []
    for name, get_conn_func, path in dbs:
        try:
            conn = get_conn_func()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = []
            for row in cursor.fetchall():
                table_name = row['name']
                cursor.execute(f"SELECT COUNT(*) as count FROM [{table_name}]")
                count = cursor.fetchone()['count']
                cursor.execute(f"PRAGMA table_info([{table_name}])")
                columns = [col['name'] for col in cursor.fetchall()]
                tables.append({
                    'name': table_name,
                    'row_count': count,
                    'columns': columns
                })
            conn.close()
            db_info.append({
                'name': name,
                'path': path,
                'tables': tables
            })
        except Exception as e:
            db_info.append({
                'name': name,
                'path': path,
                'tables': [],
                'error': str(e)
            })

    return db_info


@admin_bp.route('/table/<db_name>/<table_name>')
@require_admin
def browse_table(db_name, table_name):
    """Browse a specific table's data."""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    search = request.args.get('search', '')

    db_map = {
        'curyent.db': main_db.get_db,
        'booking.db': book_module.get_book_db,
        'probase.db': profile_module.get_probase_db,
        'chatbase.db': chat_module.get_db,
        'notibase.db': noti_module.get_db,
        'admin.db': admin_db.get_db,
    }

    get_conn_func = db_map.get(db_name)
    if not get_conn_func:
        return jsonify({'error': 'Database not found'}), 404

    try:
        conn = get_conn_func()
        cursor = conn.cursor()

        # Get columns
        cursor.execute(f"PRAGMA table_info([{table_name}])")
        columns = [col['name'] for col in cursor.fetchall()]

        # Get data
        if search:
            # Build search query across all text columns
            conditions = []
            params = []
            for col in columns:
                conditions.append(f"[{col}] LIKE ?")
                params.append(f'%{search}%')
            where_clause = f"WHERE ({' OR '.join(conditions)})"
            cursor.execute(f"SELECT * FROM [{table_name}] {where_clause} LIMIT ? OFFSET ?", params + [limit, offset])
        else:
            cursor.execute(f"SELECT * FROM [{table_name}] LIMIT ? OFFSET ?", (limit, offset))

        rows = []
        for row in cursor.fetchall():
            rows.append(dict(row))

        # Get total count
        if search:
            count_params = params.copy()
            cursor.execute(f"SELECT COUNT(*) as count FROM [{table_name}] {where_clause}", count_params)
        else:
            cursor.execute(f"SELECT COUNT(*) as count FROM [{table_name}]")
        total = cursor.fetchone()['count']

        conn.close()

        return render_template(
            'admin/browse_table.html',
            db_name=db_name,
            table_name=table_name,
            columns=columns,
            rows=rows,
            total=total,
            limit=limit,
            offset=offset,
            search=search
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/table/<db_name>/<table_name>', methods=['GET'])
@require_admin
def api_browse_table(db_name, table_name):
    """API endpoint for browsing table data (JSON)."""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    search = request.args.get('search', '')

    db_map = {
        'curyent.db': main_db.get_db,
        'booking.db': book_module.get_book_db,
        'probase.db': profile_module.get_probase_db,
        'chatbase.db': chat_module.get_db,
        'notibase.db': noti_module.get_db,
        'admin.db': admin_db.get_db,
    }

    get_conn_func = db_map.get(db_name)
    if not get_conn_func:
        return jsonify({'error': 'Database not found'}), 404

    try:
        conn = get_conn_func()
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info([{table_name}])")
        columns = [col['name'] for col in cursor.fetchall()]

        if search:
            conditions = []
            params = []
            for col in columns:
                conditions.append(f"[{col}] LIKE ?")
                params.append(f'%{search}%')
            where_clause = f"WHERE ({' OR '.join(conditions)})"
            cursor.execute(f"SELECT * FROM [{table_name}] {where_clause} LIMIT ? OFFSET ?", params + [limit, offset])
        else:
            cursor.execute(f"SELECT * FROM [{table_name}] LIMIT ? OFFSET ?", (limit, offset))

        rows = [dict(row) for row in cursor.fetchall()]

        if search:
            cursor.execute(f"SELECT COUNT(*) as count FROM [{table_name}] {where_clause}", params)
        else:
            cursor.execute(f"SELECT COUNT(*) as count FROM [{table_name}]")
        total = cursor.fetchone()['count']

        conn.close()
        return jsonify({
            'columns': columns,
            'rows': rows,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =========================
# User Management
# =========================

@admin_bp.route('/users')
@require_admin
def users():
    """List all users."""
    search = request.args.get('search', '')
    role = request.args.get('role', '')

    conn = main_db.get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if search:
        query += " AND (username LIKE ? OR email LIKE ? OR location LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    if role:
        query += " AND role = ?"
        params.append(role)

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    users_list = [dict(row) for row in cursor.fetchall()]

    # Get roles for filter
    cursor.execute("SELECT DISTINCT role FROM users ORDER BY role")
    roles = [row['role'] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'admin/users.html',
        users=users_list,
        roles=roles,
        search=search,
        role=role
    )


@admin_bp.route('/api/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user(user_id):
    """Get user details."""
    conn = main_db.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify(dict(user))
    return jsonify({'error': 'User not found'}), 404


@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@require_admin
def update_user(user_id):
    """Update a user."""
    data = request.get_json()
    conn = main_db.get_db()
    cursor = conn.cursor()

    updates = []
    values = []
    for field in ['username', 'email', 'role', 'title', 'phone', 'location', 'profile_image']:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])

    if 'password' in data and data['password']:
        from werkzeug.security import generate_password_hash
        updates.append("password = ?")
        values.append(generate_password_hash(data['password']))

    if updates:
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()

    conn.close()
    return jsonify({'success': True})


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete a user and all related data."""
    # Delete from all databases
    try:
        conn = main_db.get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

    try:
        conn = book_module.get_book_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bookings WHERE booker_id = ? OR booked_id = ?', (user_id, user_id))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

    try:
        conn = profile_module.get_probase_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM feedback WHERE user_id = ? OR from_user_id = ?', (user_id, user_id))
        cursor.execute('DELETE FROM posts WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

    try:
        conn = noti_module.get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

    return jsonify({'success': True})


# =========================
# Booking Management
# =========================

@admin_bp.route('/bookings')
@require_admin
def bookings():
    """List all bookings."""
    status = request.args.get('status', '')

    conn = book_module.get_book_db()
    cursor = conn.cursor()

    query = """
        SELECT b.*, 
               u1.username as booker_username, u1.profile_image as booker_image,
               u2.username as booked_username, u2.profile_image as booked_image, u2.role as booked_role
        FROM bookings b
        LEFT JOIN users u1 ON b.booker_id = u1.id
        LEFT JOIN users u2 ON b.booked_id = u2.id
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND b.status = ?"
        params.append(status)

    query += " ORDER BY b.created_at DESC"
    cursor.execute(query, params)
    bookings_list = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'admin/bookings.html',
        bookings=bookings_list,
        status=status
    )


@admin_bp.route('/api/bookings/<int:booking_id>', methods=['PUT'])
@require_admin
def update_booking(booking_id):
    """Update a booking's status."""
    data = request.get_json()
    conn = book_module.get_book_db()
    cursor = conn.cursor()

    updates = []
    values = []
    for field in ['status', 'approval_status', 'payout_status', 'daily_rate']:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])

    if updates:
        values.append(booking_id)
        cursor.execute(f"UPDATE bookings SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()

    conn.close()
    return jsonify({'success': True})


# =========================
# UI Settings
# =========================

@admin_bp.route('/ui-settings')
@require_admin
def ui_settings():
    """UI customization page."""
    configs = admin_db.get_all_configs()
    categories = admin_db.get_all_categories()
    return render_template('admin/ui_settings.html', configs=configs, categories=categories)


@admin_bp.route('/api/ui-config', methods=['GET'])
@require_admin
def api_get_ui_config():
    """Get UI config values (admin only)."""
    category = request.args.get('category', '')
    if category:
        configs = admin_db.get_configs_by_category(category)
    else:
        configs = admin_db.get_all_configs()
    return jsonify(configs)


# Public endpoint — used by the live site templates to read UI config
@admin_bp.route('/api/public/ui-config', methods=['GET'])
def api_public_ui_config():
    """Get all UI config values (public, no auth required)."""
    configs = admin_db.get_all_configs()
    # Flatten to key-value dict for easy template access
    flat = {}
    for category, items in configs.items():
        for item in items:
            flat[item['key']] = item['value']
    return jsonify(flat)


@admin_bp.route('/api/ui-config/<key>', methods=['PUT'])
@require_admin
def api_update_ui_config(key):
    """Update a UI config value."""
    data = request.get_json()
    value = data.get('value', '')
    admin_db.update_config(key, value)
    return jsonify({'success': True})


@admin_bp.route('/api/ui-config/batch', methods=['PUT'])
@require_admin
def api_update_ui_config_batch():
    """Update multiple UI config values at once."""
    data = request.get_json()
    for key, value in data.items():
        admin_db.update_config(key, value)
    return jsonify({'success': True})


# =========================
# System Management
# =========================

@admin_bp.route('/system')
@require_admin
def system():
    """System management page."""
    return render_template('admin/system.html')


@admin_bp.route('/api/reset-databases', methods=['POST'])
@require_admin
def api_reset_databases():
    """Reset all databases."""
    try:
        from curyent import reset_all_databases
        success, failed = reset_all_databases()
        return jsonify({
            'success': True,
            'reset_success': success,
            'reset_failed': failed
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/ui-config/reset', methods=['POST'])
@require_admin
def api_reset_ui_config():
    """Reset all UI config to defaults."""
    try:
        # Delete and recreate the ui_config table
        conn = admin_db.get_db()
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS ui_config')
        conn.commit()
        conn.close()
        admin_db.init_db()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
