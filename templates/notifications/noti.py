import sqlite3
import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session

# Notifications database file path (centralized in base folder)
NOTI_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'notibase.db')


def get_db():
    """Get a connection to the notifications database."""
    conn = sqlite3.connect(NOTI_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_db():
    """Delete and recreate the notifications database from scratch, clearing all data.
    If the file is locked, drop all tables instead of deleting the file."""
    if os.path.exists(NOTI_DB_PATH):
        try:
            os.remove(NOTI_DB_PATH)
        except PermissionError:
            # File is locked — drop all tables to clear data in place
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table['name']}")
            conn.commit()
            conn.close()
    init_db()


def init_db():
    """Initialize the notifications database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if old schema exists (without user_id column) and drop it
    try:
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [row['name'] for row in cursor.fetchall()]
        if 'user_id' not in columns:
            # Old schema — drop it so we can recreate with new schema
            cursor.execute("DROP TABLE IF EXISTS notifications")
            cursor.execute("DROP TABLE IF EXISTS user_notifications")
    except Exception:
        pass

    # Notifications table — per-user notifications matching the guideline schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT NOT NULL DEFAULT 'system',
            related_item_id INTEGER,
            priority TEXT NOT NULL DEFAULT 'low',
            action_url TEXT,
            action_label TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Index for fast user queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id, is_read, created_at)
    ''')

    conn.commit()
    conn.close()


# =========================
# Notification Types
# =========================

NOTIFICATION_TYPES = {
    # Social Notifications
    'new_follower': {'icon': 'fa-user-plus', 'color': '#c9a0ff'},
    'new_friend': {'icon': 'fa-user-check', 'color': '#34d399'},

    # Booking Notifications
    'booking_request': {'icon': 'fa-book', 'color': '#60a5fa'},
    'booking_accepted': {'icon': 'fa-check-circle', 'color': '#34d399'},
    'booking_declined': {'icon': 'fa-times-circle', 'color': '#f87171'},
    'booking_updated': {'icon': 'fa-calendar-check', 'color': '#fbbf24'},
    'booking_cancelled': {'icon': 'fa-ban', 'color': '#f87171'},

    # Payment Notifications
    'payment_received': {'icon': 'fa-credit-card', 'color': '#34d399'},
    'payment_deposit': {'icon': 'fa-coins', 'color': '#fbbf24'},
    'payment_pending': {'icon': 'fa-clock', 'color': '#fbbf24'},
    'payment_failed': {'icon': 'fa-exclamation-circle', 'color': '#f87171'},

    # Event Notifications
    'event_confirmed': {'icon': 'fa-party-horn', 'color': '#34d399'},
    'event_reminder': {'icon': 'fa-clock', 'color': '#f87171'},
    'event_venue_changed': {'icon': 'fa-location-dot', 'color': '#fbbf24'},
    'event_schedule_updated': {'icon': 'fa-calendar-days', 'color': '#60a5fa'},

    # Communication Notifications
    'new_message': {'icon': 'fa-comment-dots', 'color': '#60a5fa'},
    'new_inquiry': {'icon': 'fa-envelope', 'color': '#60a5fa'},
    'new_review': {'icon': 'fa-star', 'color': '#fbbf24'},

    # Account Notifications
    'password_changed': {'icon': 'fa-lock', 'color': '#fbbf24'},
    'profile_approved': {'icon': 'fa-circle-check', 'color': '#34d399'},
    'profile_update_required': {'icon': 'fa-exclamation-triangle', 'color': '#f87171'},

    # System/General
    'system': {'icon': 'fa-bell', 'color': '#c9a0ff'},
}

PRIORITY_LEVELS = ['high', 'medium', 'low']


# =========================
# Notification Helpers
# =========================

def get_user_notifications(user_id):
    """Get all notifications for a user, ordered by read status and time."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY is_read ASC, created_at DESC
    ''', (user_id,))

    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Enrich with type info
    for notif in notifications:
        ntype = notif.get('notification_type', 'system')
        type_info = NOTIFICATION_TYPES.get(ntype, NOTIFICATION_TYPES['system'])
        notif['icon'] = type_info['icon']
        notif['color'] = type_info['color']

    return notifications


def get_unread_count(user_id):
    """Get the count of unread notifications for a user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COUNT(*) as count FROM notifications
        WHERE user_id = ? AND is_read = 0
    ''', (user_id,))

    count = cursor.fetchone()['count']
    conn.close()
    return count


def mark_as_read(user_id, notification_id):
    """Mark a single notification as read."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE notifications
        SET is_read = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (notification_id, user_id))

    conn.commit()
    conn.close()


def mark_all_as_read(user_id):
    """Mark all notifications as read for a user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE notifications
        SET is_read = 1, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND is_read = 0
    ''', (user_id,))

    conn.commit()
    conn.close()


def create_notification(user_id, title, message, notification_type='system',
                        related_item_id=None, priority='low', action_url=None, action_label=None):
    """Create a new notification for a user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO notifications (user_id, title, message, notification_type, related_item_id,
                                    priority, action_url, action_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, title, message, notification_type, related_item_id, priority, action_url, action_label))

    conn.commit()
    notif_id = cursor.lastrowid
    conn.close()
    return notif_id


def delete_notification(user_id, notification_id):
    """Delete a notification for a user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM notifications WHERE id = ? AND user_id = ?
    ''', (notification_id, user_id))

    conn.commit()
    conn.close()


def group_notifications_by_time(notifications):
    """Group notifications by time periods: Today, Yesterday, This Week, Earlier."""
    now = datetime.now()
    today = []
    yesterday = []
    this_week = []
    earlier = []

    for notif in notifications:
        created = datetime.strptime(notif['created_at'], '%Y-%m-%d %H:%M:%S')
        diff = now - created

        if diff.days == 0:
            today.append(notif)
        elif diff.days == 1:
            yesterday.append(notif)
        elif diff.days < 7:
            this_week.append(notif)
        else:
            earlier.append(notif)

    groups = []
    if today:
        groups.append({'label': 'Today', 'notifications': today})
    if yesterday:
        groups.append({'label': 'Yesterday', 'notifications': yesterday})
    if this_week:
        groups.append({'label': 'This Week', 'notifications': this_week})
    if earlier:
        groups.append({'label': 'Earlier', 'notifications': earlier})

    return groups


def format_time_ago(created_at_str):
    """Format a timestamp as relative time (e.g., '2 minutes ago')."""
    created = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    diff = now - created

    if diff.seconds < 60:
        return 'Just now'
    elif diff.seconds < 3600:
        minutes = diff.seconds // 60
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif diff.seconds < 86400:
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif diff.days == 1:
        return 'Yesterday'
    elif diff.days < 7:
        return f'{diff.days} day{"s" if diff.days != 1 else ""} ago'
    elif diff.days < 30:
        weeks = diff.days // 7
        return f'{weeks} week{"s" if weeks != 1 else ""} ago'
    else:
        return created.strftime('%b %d, %Y')


# =========================
# Notifications API Routes
# =========================

noti_api_bp = Blueprint('noti_api', __name__)


@noti_api_bp.route('/api/notifications', methods=['GET'])
def api_get_notifications():
    """API: Get all notifications for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    notifications = get_user_notifications(user_id)
    groups = group_notifications_by_time(notifications)

    # Add time-ago formatting
    for group in groups:
        for notif in group['notifications']:
            notif['time_ago'] = format_time_ago(notif['created_at'])

    return jsonify({'success': True, 'groups': groups, 'total': len(notifications)})


@noti_api_bp.route('/api/notifications/unread-count', methods=['GET'])
def api_get_unread_count():
    """API: Get the count of unread notifications for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    count = get_unread_count(user_id)
    return jsonify({'success': True, 'unread_count': count})


@noti_api_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
def api_mark_as_read(notif_id):
    """API: Mark a notification as read."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    mark_as_read(user_id, notif_id)
    return jsonify({'success': True})


@noti_api_bp.route('/api/notifications/mark-all-read', methods=['POST'])
def api_mark_all_read():
    """API: Mark all notifications as read."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    mark_all_as_read(user_id)
    return jsonify({'success': True})


@noti_api_bp.route('/api/notifications/create', methods=['POST'])
def api_create_notification():
    """API: Create a new notification for a user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    title = data.get('title', '').strip()
    message = data.get('message', '').strip()
    notification_type = data.get('notification_type', 'system')
    related_item_id = data.get('related_item_id')
    priority = data.get('priority', 'low')
    action_url = data.get('action_url')
    action_label = data.get('action_label')

    if not title or not message:
        return jsonify({'success': False, 'message': 'Title and message are required'}), 400

    notif_id = create_notification(user_id, title, message, notification_type,
                                   related_item_id, priority, action_url, action_label)
    return jsonify({'success': True, 'notification_id': notif_id})


@noti_api_bp.route('/api/notifications/<int:notif_id>', methods=['DELETE'])
def api_delete_notification(notif_id):
    """API: Delete a notification."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    delete_notification(user_id, notif_id)
    return jsonify({'success': True})
