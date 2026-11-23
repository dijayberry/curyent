"""
Social module — friends, followers, and user review page.
"""
import sqlite3
import os
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for

# Import the main db module to read user data
import templates.account.db as main_db
# Import the profile module for posts and feedback
import templates.profile.profile as profile_module
# Import notification module for follow/friend notifications
import templates.notifications.noti as noti_module
# Import chat module for sending welcome messages
import templates.chat.chat as chat_module

social_bp = Blueprint('social', __name__)

# Database file path for social relationships
SOCIAL_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'social.db')


def get_social_db():
    """Get a connection to the social database."""
    conn = sqlite3.connect(SOCIAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_social_db():
    """Initialize the social database tables."""
    conn = get_social_db()
    cursor = conn.cursor()

    # Friends table — stores follow/friend relationships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'following',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (friend_id) REFERENCES users(id),
            UNIQUE(user_id, friend_id)
        )
    ''')

    # Sync users table from curyent.db
    try:
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT * FROM users')
        users = main_cursor.fetchall()
        main_conn.close()

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
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN profile_image TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN title TEXT DEFAULT ''")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        cursor.execute('DELETE FROM users')
        for u in users:
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, username, email, password, role, title, phone, location, profile_image, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (u['id'], u['username'], u['email'], u['password'], u['role'], u['title'], u['phone'], u['location'], u['profile_image'], u['created_at']))
        conn.commit()
    except Exception:
        pass

    conn.close()


# =========================
# Data Helpers
# =========================

def get_following(user_id):
    """Get list of users that the given user is following (not mutual friends)."""
    conn = get_social_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.*, f.status
        FROM friends f
        JOIN users u ON f.friend_id = u.id
        WHERE f.user_id = ? AND f.status = 'following'
        ORDER BY f.created_at DESC
    ''', (user_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_followers(user_id):
    """Get list of users who are following the given user (not mutual friends)."""
    conn = get_social_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.*, f.status
        FROM friends f
        JOIN users u ON f.user_id = u.id
        WHERE f.friend_id = ? AND f.status = 'following'
        ORDER BY f.created_at DESC
    ''', (user_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_friends(user_id):
    """Get mutual friends (both ways followed)."""
    conn = get_social_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.*, f.status
        FROM friends f
        JOIN users u ON f.friend_id = u.id
        WHERE f.user_id = ? AND f.status = 'friends'
        ORDER BY f.created_at DESC
    ''', (user_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_all_users(exclude_id=None, search_query=None):
    """Get all users for the Find tab."""
    conn = get_social_db()
    cursor = conn.cursor()
    if search_query:
        cursor.execute('''
            SELECT id, username, location, profile_image, title, role
            FROM users
            WHERE id != ?
              AND (LOWER(username) LIKE ? OR LOWER(location) LIKE ? OR LOWER(COALESCE(title, '')) LIKE ?)
            ORDER BY username ASC
            LIMIT 50
        ''', (exclude_id, f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute('''
            SELECT id, username, location, profile_image, title, role
            FROM users
            WHERE id != ?
            ORDER BY username ASC
            LIMIT 50
        ''', (exclude_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_relationship(user_id, target_id):
    """Get the relationship status between two users."""
    conn = get_social_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT status FROM friends
        WHERE user_id = ? AND friend_id = ?
    ''', (user_id, target_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['status']
    return None


def get_user_by_id(user_id):
    """Get a user by ID."""
    conn = get_social_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None


# =========================
# Routes
# =========================

@social_bp.route('/friends')
def friends_page():
    """Render the friends page."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('account.logi'))

    return render_template('social/friends.html', user_id=user_id)


@social_bp.route('/review/<int:user_id>')
def review_page(user_id):
    """Render the review page for viewing another user's profile."""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('account.logi'))

    # Get the user being reviewed
    reviewed_user = get_user_by_id(user_id)
    if not reviewed_user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # Get relationship status
    relationship = get_relationship(current_user_id, user_id)

    # Get posts for this user
    posts = profile_module.get_posts_for_user(user_id)

    # Get ranking stats for this user
    stats = profile_module.get_ranking_stats(user_id)

    # Get feedback for this user
    feedback = profile_module.get_feedback_for_me(user_id)

    return render_template('social/review.html',
                           reviewed_user=reviewed_user,
                           relationship=relationship,
                           posts=posts,
                           stats=stats,
                           feedback=feedback,
                           current_user_id=current_user_id)


# =========================
# API Routes
# =========================

@social_bp.route('/api/friends/following', methods=['GET'])
def api_get_following():
    """API: Get list of users the current user is following."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    following = get_following(user_id)
    return jsonify({'success': True, 'users': following})


@social_bp.route('/api/friends/followers', methods=['GET'])
def api_get_followers():
    """API: Get list of users who follow the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    followers = get_followers(user_id)
    return jsonify({'success': True, 'users': followers})


@social_bp.route('/api/friends/mutual', methods=['GET'])
def api_get_friends():
    """API: Get mutual friends."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    friends = get_friends(user_id)
    return jsonify({'success': True, 'users': friends})


@social_bp.route('/api/friends/find', methods=['GET'])
def api_find_users():
    """API: Find users (for the Find tab)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    search_query = request.args.get('q', '').strip().lower()
    users = get_all_users(exclude_id=user_id, search_query=search_query if search_query else None)

    # Add relationship status for each user
    for user in users:
        user['relationship'] = get_relationship(user_id, user['id'])

    return jsonify({'success': True, 'users': users})


@social_bp.route('/api/friends/search', methods=['GET'])
def api_search_users():
    """API: Search users by username or location."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify({'success': True, 'users': []})

    conn = get_social_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, location, profile_image, title, role
        FROM users
        WHERE id != ?
          AND (LOWER(username) LIKE ? OR LOWER(location) LIKE ? OR LOWER(COALESCE(title, '')) LIKE ?)
        ORDER BY username ASC
        LIMIT 20
    ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Add relationship status
    for user in users:
        user['relationship'] = get_relationship(user_id, user['id'])

    return jsonify({'success': True, 'users': users})


@social_bp.route('/api/friends/follow', methods=['POST'])
def api_follow():
    """API: Follow a user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    target_id = data.get('target_id')
    if not target_id:
        return jsonify({'success': False, 'message': 'Target user ID required'}), 400

    if str(target_id) == str(user_id):
        return jsonify({'success': False, 'message': 'Cannot follow yourself'}), 400

    conn = get_social_db()
    cursor = conn.cursor()

    # Check if already following
    cursor.execute('SELECT status FROM friends WHERE user_id = ? AND friend_id = ?', (user_id, target_id))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Already following this user'}), 400

    # Check if the target is following the current user (for friends status)
    cursor.execute('SELECT status FROM friends WHERE user_id = ? AND friend_id = ?', (target_id, user_id))
    reverse = cursor.fetchone()

    # Get usernames for notifications and messages
    main_conn = main_db.get_db()
    main_cursor = main_conn.cursor()
    main_cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    follower_row = main_cursor.fetchone()
    follower_username = follower_row['username'] if follower_row else 'Someone'

    main_cursor.execute('SELECT username FROM users WHERE id = ?', (target_id,))
    target_row = main_cursor.fetchone()
    target_username = target_row['username'] if target_row else 'Someone'
    main_conn.close()

    if reverse:
        # Both following each other — set as friends
        status = 'friends'
        cursor.execute('UPDATE friends SET status = ? WHERE user_id = ? AND friend_id = ?', ('friends', target_id, user_id))

        # Notify the person who followed first: "You are now friends with {follower_username}"
        try:
            noti_module.create_notification(
                user_id=target_id,
                title='New Friend!',
                message=f'{follower_username} followed back. You are now friends!',
                notification_type='new_friend',
                related_item_id=user_id,
                priority='medium',
                action_url='/review/' + str(user_id),
                action_label='View Profile'
            )
        except Exception:
            pass

        # Send welcome chat message to the person who followed first
        try:
            conv_id = chat_module.get_or_create_conversation(user_id, target_id)
            welcome_msg = f'🎉 Hey {target_username}! We are now friends on CURYENT! Feel free to chat and connect. Let\'s engage more! 🚀'
            chat_module.send_message(conv_id, user_id, welcome_msg)

            # Also notify about the new message
            noti_module.create_notification(
                user_id=target_id,
                title='New message',
                message=f'{follower_username}: {welcome_msg[:100]}',
                notification_type='new_message',
                related_item_id=conv_id,
                priority='low',
                action_url='/chat',
                action_label='Reply'
            )
        except Exception:
            pass
    else:
        status = 'following'

        # Notify the target: "{follower_username} started following you"
        try:
            noti_module.create_notification(
                user_id=target_id,
                title='New Follower',
                message=f'{follower_username} started following you. Follow back to become friends!',
                notification_type='new_follower',
                related_item_id=user_id,
                priority='medium',
                action_url='/review/' + str(user_id),
                action_label='Follow Back'
            )
        except Exception:
            pass

    cursor.execute('''
        INSERT INTO friends (user_id, friend_id, status)
        VALUES (?, ?, ?)
    ''', (user_id, target_id, status))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'status': status, 'message': 'Friends!' if status == 'friends' else 'Now following'})


@social_bp.route('/api/friends/unfollow', methods=['POST'])
def api_unfollow():
    """API: Unfollow a user (remove from friends or following)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    target_id = data.get('target_id')
    if not target_id:
        return jsonify({'success': False, 'message': 'Target user ID required'}), 400

    conn = get_social_db()
    cursor = conn.cursor()

    # Check current status before deleting
    cursor.execute('SELECT status FROM friends WHERE user_id = ? AND friend_id = ?', (user_id, target_id))
    current_status = cursor.fetchone()

    cursor.execute('DELETE FROM friends WHERE user_id = ? AND friend_id = ?', (user_id, target_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    if not deleted:
        return jsonify({'success': False, 'message': 'Not following this user'}), 400

    # If it was a mutual friend, notify the other person
    if current_status and current_status['status'] == 'friends':
        # Also remove the reverse relationship (they are no longer friends)
        conn = get_social_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM friends WHERE user_id = ? AND friend_id = ?', (target_id, user_id))
        conn.commit()
        conn.close()

        # Get usernames for notification
        try:
            main_conn = main_db.get_db()
            main_cursor = main_conn.cursor()
            main_cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            unfollower_row = main_cursor.fetchone()
            unfollower_username = unfollower_row['username'] if unfollower_row else 'Someone'

            main_cursor.execute('SELECT username FROM users WHERE id = ?', (target_id,))
            target_row = main_cursor.fetchone()
            target_username = target_row['username'] if target_row else 'Someone'
            main_conn.close()

            noti_module.create_notification(
                user_id=target_id,
                title='Friend Removed',
                message=f'{unfollower_username} is no longer your friend.',
                notification_type='system',
                related_item_id=user_id,
                priority='low',
                action_url='/review/' + str(user_id),
                action_label='View Profile'
            )
        except Exception:
            pass

    return jsonify({'success': True, 'message': 'Unfollowed'})


@social_bp.route('/api/friends/relationship', methods=['GET'])
def api_get_relationship():
    """API: Get relationship status with a specific user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    target_id = request.args.get('target_id')
    if not target_id:
        return jsonify({'success': False, 'message': 'Target user ID required'}), 400

    relationship = get_relationship(user_id, int(target_id))
    return jsonify({'success': True, 'relationship': relationship})


@social_bp.route('/api/friends/count', methods=['GET'])
def api_get_counts():
    """API: Get friend/follower/following counts."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    friends = get_friends(user_id)
    following = get_following(user_id)
    followers = get_followers(user_id)

    return jsonify({
        'success': True,
        'friends': len(friends),
        'following': len(following),
        'followers': len(followers)
    })
