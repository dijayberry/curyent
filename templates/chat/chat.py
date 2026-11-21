import sqlite3
import os
from flask import Blueprint, render_template, jsonify, request, session

# Chat database file path (centralized in base folder)
CHAT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'chatbase.db')

# Import notification helper to create automatic notifications
import templates.notifications.noti as noti_module


def get_db():
    """Get a connection to the chat database."""
    conn = sqlite3.connect(CHAT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_db():
    """Delete and recreate the chat database from scratch, clearing all data.
    If the file is locked, drop all tables instead of deleting the file."""
    if os.path.exists(CHAT_DB_PATH):
        try:
            os.remove(CHAT_DB_PATH)
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
    """Initialize the chat database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Conversations table — tracks conversations between two users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user1_id) REFERENCES users(id),
            FOREIGN KEY (user2_id) REFERENCES users(id),
            UNIQUE(user1_id, user2_id)
        )
    ''')

    # Messages table — stores individual messages within a conversation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# =========================
# Conversation Helpers
# =========================

def get_or_create_conversation(user_id, other_user_id):
    """Get or create a conversation between two users."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if conversation already exists (either order)
    cursor.execute('''
        SELECT id FROM conversations
        WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
    ''', (user_id, other_user_id, other_user_id, user_id))

    row = cursor.fetchone()
    if row:
        conv_id = row['id']
        conn.close()
        return conv_id

    # Create new conversation
    cursor.execute('''
        INSERT INTO conversations (user1_id, user2_id)
        VALUES (?, ?)
    ''', (user_id, other_user_id))
    conn.commit()
    conv_id = cursor.lastrowid
    conn.close()
    return conv_id


def get_conversations_for_user(user_id):
    """Get all conversations for a user with the other participant's info and last message."""
    import templates.account.db as main_db

    conn = get_db()
    cursor = conn.cursor()

    # Get all conversations involving this user
    cursor.execute('''
        SELECT c.id, c.user1_id, c.user2_id
        FROM conversations c
        WHERE c.user1_id = ? OR c.user2_id = ?
        ORDER BY c.created_at DESC
    ''', (user_id, user_id))

    conversations = cursor.fetchall()
    result = []

    for conv in conversations:
        conv_id = conv['id']
        other_user_id = conv['user2_id'] if conv['user1_id'] == user_id else conv['user1_id']

        # Get the other user's info
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()
        main_cursor.execute('SELECT id, username, role, title, location, profile_image FROM users WHERE id = ?', (other_user_id,))
        other_user = main_cursor.fetchone()
        main_conn.close()

        if not other_user:
            continue

        other_user_dict = dict(other_user)

        # Get last message in this conversation
        cursor.execute('''
            SELECT m.text, m.created_at, m.is_read
            FROM messages m
            WHERE m.conversation_id = ?
            ORDER BY m.created_at DESC
            LIMIT 1
        ''', (conv_id,))
        last_msg = cursor.fetchone()

        # Get unread count for this user
        cursor.execute('''
            SELECT COUNT(*) as count FROM messages
            WHERE conversation_id = ? AND sender_id != ? AND is_read = 0
        ''', (conv_id, user_id))
        unread_count = cursor.fetchone()['count']

        result.append({
            'conversation_id': conv_id,
            'other_user_id': other_user_id,
            'username': other_user_dict['username'],
            'role': other_user_dict['role'],
            'title': other_user_dict.get('title', ''),
            'location': other_user_dict.get('location', ''),
            'profile_image': other_user_dict.get('profile_image', ''),
            'last_message': last_msg['text'] if last_msg else '',
            'last_message_time': last_msg['created_at'] if last_msg else '',
            'unread': unread_count,
        })

    conn.close()
    return result


# =========================
# Message Helpers
# =========================

def get_messages(conversation_id):
    """Get all messages for a conversation."""
    import templates.account.db as main_db

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT m.id, m.sender_id, m.text, m.is_read, m.created_at
        FROM messages m
        WHERE m.conversation_id = ?
        ORDER BY m.created_at ASC
    ''', (conversation_id,))

    messages = cursor.fetchall()
    result = []

    main_conn = main_db.get_db()
    main_cursor = main_conn.cursor()

    for msg in messages:
        main_cursor.execute('SELECT username FROM users WHERE id = ?', (msg['sender_id'],))
        sender = main_cursor.fetchone()

        result.append({
            'id': msg['id'],
            'sender_id': msg['sender_id'],
            'sender_name': sender['username'] if sender else 'Unknown',
            'text': msg['text'],
            'is_read': msg['is_read'],
            'created_at': msg['created_at'],
        })

    main_conn.close()
    conn.close()
    return result


def send_message(conversation_id, sender_id, text):
    """Send a new message in a conversation."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO messages (conversation_id, sender_id, text)
        VALUES (?, ?, ?)
    ''', (conversation_id, sender_id, text))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


def mark_messages_as_read(conversation_id, user_id):
    """Mark all messages in a conversation as read for the given user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE messages SET is_read = 1
        WHERE conversation_id = ? AND sender_id != ? AND is_read = 0
    ''', (conversation_id, user_id))
    conn.commit()
    conn.close()


# =========================
# User Listing Helpers
# =========================

def get_all_users(exclude_user_id=None):
    """Get all users from the main database (for contact list)."""
    import templates.account.db as main_db

    conn = main_db.get_db()
    cursor = conn.cursor()

    if exclude_user_id:
        cursor.execute('SELECT id, username, role, title, location, profile_image FROM users WHERE id != ?', (exclude_user_id,))
    else:
        cursor.execute('SELECT id, username, role, title, location, profile_image FROM users')

    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


# =========================
# Chat API Routes
# =========================

chat_api_bp = Blueprint('chat_api', __name__)


@chat_api_bp.route('/api/chat/conversations', methods=['GET'])
def api_get_conversations():
    """API: Get all conversations for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conversations = get_conversations_for_user(user_id)
    return jsonify({'success': True, 'conversations': conversations})


@chat_api_bp.route('/api/chat/users', methods=['GET'])
def api_get_users():
    """API: Get all users (for starting new conversations)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    users = get_all_users(exclude_user_id=user_id)
    return jsonify({'success': True, 'users': users})


@chat_api_bp.route('/api/chat/messages/<int:other_user_id>', methods=['GET'])
def api_get_messages(other_user_id):
    """API: Get messages with a specific user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    # Get or create conversation
    conversation_id = get_or_create_conversation(user_id, other_user_id)

    # Get messages
    messages = get_messages(conversation_id)

    # Mark messages as read
    mark_messages_as_read(conversation_id, user_id)

    return jsonify({'success': True, 'messages': messages, 'conversation_id': conversation_id})


@chat_api_bp.route('/api/chat/send', methods=['POST'])
def api_send_message():
    """API: Send a message to a specific user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    other_user_id = data.get('to_user_id')
    text = data.get('text', '').strip()

    if not other_user_id or not text:
        return jsonify({'success': False, 'message': 'Missing recipient or message text'}), 400

    # Get or create conversation
    conversation_id = get_or_create_conversation(user_id, other_user_id)

    # Send message
    msg_id = send_message(conversation_id, user_id, text)

    # Notify the recipient about the new message
    try:
        import templates.account.db as main_db
        main_conn = main_db.get_db()
        main_cursor = main_conn.cursor()

        # Get sender's username
        main_cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        sender = main_cursor.fetchone()
        sender_name = sender['username'] if sender else 'Someone'

        # Get recipient's username
        main_cursor.execute('SELECT username FROM users WHERE id = ?', (other_user_id,))
        recipient = main_cursor.fetchone()
        main_conn.close()

        # Truncate message preview to 100 chars
        preview = text[:100] + ('...' if len(text) > 100 else '')

        noti_module.create_notification(
            user_id=other_user_id,
            title='New message',
            message=f'{sender_name}: {preview}',
            notification_type='new_message',
            related_item_id=conversation_id,
            priority='low',
            action_url='/chat',
            action_label='Reply'
        )
    except Exception:
        pass

    return jsonify({'success': True, 'message_id': msg_id, 'conversation_id': conversation_id})


@chat_api_bp.route('/api/chat/unread-total', methods=['GET'])
def api_get_unread_total():
    """API: Get total unread message count for the current user across all conversations."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    conn = get_db()
    cursor = conn.cursor()

    # Sum all unread messages across all conversations where the user is a participant
    cursor.execute('''
        SELECT COUNT(*) as total FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE m.sender_id != ? AND m.is_read = 0
          AND (c.user1_id = ? OR c.user2_id = ?)
    ''', (user_id, user_id, user_id))

    total = cursor.fetchone()['total']
    conn.close()

    return jsonify({'success': True, 'unread_total': total})
