"""
Admin database module — manages the admin configuration database.
Stores UI customization settings and admin credentials.
"""
import sqlite3
import os

# Admin database file path
ADMIN_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'base', 'admin.db')

# Default admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = '$2b$12$LJ3m4U3ua4a2evBwzaq5uOqRzArAlzIqRZ0G9dVj5xW5pGFiT.FzG'  # Password: 'curyentadmin'
ADMIN_PASSWORD_PLAIN = 'curyentadmin'  # Stored for simple comparison


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(ADMIN_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the admin database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # UI Config table — stores customizable UI elements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ui_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Admin settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL
        )
    ''')

    # Seed default UI config values if table is empty
    cursor.execute('SELECT COUNT(*) as count FROM ui_config')
    if cursor.fetchone()['count'] == 0:
        default_configs = [
            # Navigation labels
            ('nav_home_label', 'Home', 'navigation', 'Home button label'),
            ('nav_bookings_label', 'Bookings', 'navigation', 'Bookings button label'),
            ('nav_chat_label', 'Chat', 'navigation', 'Chat button label'),
            ('nav_notifications_label', 'Notifications', 'navigation', 'Notifications button label'),
            ('nav_friends_label', 'Friends', 'navigation', 'Friends button label'),
            ('nav_account_label', 'Account', 'navigation', 'Account button label'),
            ('nav_signin_label', 'Sign In', 'navigation', 'Sign In button label'),
            ('nav_menu_label', 'Menu', 'navigation', 'Menu button label'),

            # Home page section titles
            ('home_djs_title', 'DJs', 'home_sections', 'DJs section title'),
            ('home_djs_description', 'Find the best DJs for your event', 'home_sections', 'DJs section description'),
            ('home_venues_title', 'Venues', 'home_sections', 'Venues section title'),
            ('home_venues_description', 'Discover amazing venues', 'home_sections', 'Venues section description'),
            ('home_photographers_title', 'Photographers', 'home_sections', 'Photographers section title'),
            ('home_photographers_description', 'Capture your special moments', 'home_sections', 'Photographers section description'),
            ('home_tents_title', 'Tents', 'home_sections', 'Tents section title'),
            ('home_tents_description', 'Tent rental services for your event', 'home_sections', 'Tents section description'),
            ('home_caterer_title', 'Caterer', 'home_sections', 'Caterer section title'),
            ('home_caterer_description', 'Delicious catering for your event', 'home_sections', 'Caterer section description'),

            # Home page dropdown labels
            ('home_dropdown_djs', 'DJs', 'home_sections', 'Dropdown: DJs label'),
            ('home_dropdown_venues', 'Venues', 'home_sections', 'Dropdown: Venues label'),
            ('home_dropdown_photographers', 'Photographers', 'home_sections', 'Dropdown: Photographers label'),
            ('home_dropdown_tents', 'Tents', 'home_sections', 'Dropdown: Tents label'),
            ('home_dropdown_caterer', 'Caterer', 'home_sections', 'Dropdown: Caterer label'),

            # Role selection labels
            ('role_choose_title', 'Choose Your Role', 'role_selection', 'Role selection page title'),
            ('role_client_label', 'Client', 'role_selection', 'Client role label'),
            ('role_dj_label', 'DJ', 'role_selection', 'DJ role label'),
            ('role_venue_label', 'Venue', 'role_selection', 'Venue role label'),
            ('role_photographer_label', 'Photographer', 'role_selection', 'Photographer role label'),
            ('role_tents_label', 'Tents', 'role_selection', 'Tents role label'),
            ('role_caterer_label', 'Caterer', 'role_selection', 'Caterer role label'),

            # Button labels
            ('btn_view_all', 'View All', 'buttons', 'View All button text'),
            ('btn_close', 'Close', 'buttons', 'Close button text'),
            ('btn_book_now', 'Book Now', 'buttons', 'Book Now button text'),
            ('btn_search', 'Search', 'buttons', 'Search button text'),
            ('btn_send', 'Send', 'buttons', 'Send button text'),
            ('btn_save', 'Save', 'buttons', 'Save button text'),
            ('btn_cancel', 'Cancel', 'buttons', 'Cancel button text'),
            ('btn_delete', 'Delete', 'buttons', 'Delete button text'),
            ('btn_edit', 'Edit', 'buttons', 'Edit button text'),

            # Search placeholder
            ('search_placeholder', 'Search DJs, Events, Photographers, Tents...', 'general', 'Search bar placeholder text'),

            # Site branding
            ('site_title', 'CURYENT - Event Networking', 'branding', 'Browser tab title'),
            ('site_name', 'CURYENT', 'branding', 'Site name/logo text'),

            # Loading messages
            ('loading_djs', 'Loading DJs...', 'loading', 'DJs loading message'),
            ('loading_venues', 'Loading Venues...', 'loading', 'Venues loading message'),
            ('loading_photographers', 'Loading Photographers...', 'loading', 'Photographers loading message'),
            ('loading_tents', 'Loading Tents...', 'loading', 'Tents loading message'),
            ('loading_caterers', 'Loading Caterers...', 'loading', 'Caterers loading message'),

            # Color settings (CSS variables)
            ('color_primary', '#6366f1', 'colors', 'Primary brand color'),
            ('color_secondary', '#8b5cf6', 'colors', 'Secondary brand color'),
            ('color_background', '#0f172a', 'colors', 'Background color'),
            ('color_text', '#e2e8f0', 'colors', 'Text color'),
            ('color_button_bg', '#6366f1', 'colors', 'Button background color'),
            ('color_button_text', '#ffffff', 'colors', 'Button text color'),
        ]
        for key, value, category, description in default_configs:
            cursor.execute(
                'INSERT INTO ui_config (key, value, category, description) VALUES (?, ?, ?, ?)',
                (key, value, category, description)
            )

    conn.commit()
    conn.close()


def get_config(key):
    """Get a UI config value by key."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM ui_config WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['value']
    return None


def get_all_configs():
    """Get all UI config values grouped by category."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value, category, description FROM ui_config ORDER BY category, key')
    rows = cursor.fetchall()
    conn.close()

    configs = {}
    for row in rows:
        category = row['category']
        if category not in configs:
            configs[category] = []
        configs[category].append({
            'key': row['key'],
            'value': row['value'],
            'description': row['description']
        })
    return configs


def get_configs_by_category(category):
    """Get UI config values for a specific category."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value, category, description FROM ui_config WHERE category = ? ORDER BY key', (category,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        'key': row['key'],
        'value': row['value'],
        'description': row['description']
    } for row in rows]


def update_config(key, value):
    """Update a UI config value."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE ui_config SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?',
        (value, key)
    )
    conn.commit()
    conn.close()


def reset_config(key):
    """Reset a config value to its default (re-initialize the whole table)."""
    init_db()


def verify_admin_password(password):
    """Verify admin password. Simple comparison for the admin panel."""
    return password == ADMIN_PASSWORD_PLAIN


def get_all_categories():
    """Get all unique categories from ui_config."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM ui_config ORDER BY category')
    rows = cursor.fetchall()
    conn.close()
    return [row['category'] for row in rows]
