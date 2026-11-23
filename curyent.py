import os
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, session, request, jsonify
from templates.account import account_bp
from templates.book import book_bp
from templates.profile import profile_bp
from templates.chat import chat_bp
from templates.notifications import notifications_bp
from templates.admin import admin_bp
from templates.social import social_bp

app = Flask(__name__)
app.secret_key = 'curyent-secret-key'
app.register_blueprint(account_bp)
app.register_blueprint(book_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(social_bp)


@app.after_request
def inject_page_loader(response):
    """Inject the CURYENT page loader CSS and JS into all HTML responses."""
    if response.content_type and 'text/html' in response.content_type:
        try:
            # Only inject for non-admin pages (admin has its own styling)
            path = request.path
            if not path.startswith('/admin') and not path.startswith('/friends') and not path.startswith('/review') and not path.startswith('/api/friends'):
                loader_css = '<link rel="stylesheet" href="/static/css/loader.css">'
                loader_js = r'<script src="/static/js/loader.js"></script>'
                
                html = response.get_data(as_text=True)
                
                # Inject CSS right before </head>
                if '</head>' in html:
                    html = html.replace('</head>', loader_css + '\n</head>')
                
                # Inject JS right after <body>
                if '<body>' in html:
                    html = html.replace('<body>', '<body>' + loader_js)
                
                response.set_data(html.encode('utf-8'))
        except Exception:
            # If injection fails, continue without the loader
            pass
    return response

@app.route('/')
def home():
    user_id = session.get('user_id')
    username = session.get('username', '')
    location = ''
    profile_image = ''
    title = ''
    if user_id:
        import templates.account.db as db
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT location, profile_image, title FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            location = row['location'] or ''
            profile_image = row['profile_image'] or ''
            title = row['title'] or ''
        conn.close()

    # Load UI config from admin.db for dynamic home page
    import templates.admin.admin_db as admin_db
    ui_config = {}
    try:
        all_configs = admin_db.get_all_configs()
        for category, items in all_configs.items():
            for item in items:
                ui_config[item['key']] = item['value']
    except Exception:
        pass

    return render_template('home/home.html', logged_in=user_id is not None, username=username, location=location, profile_image=profile_image, title=title, ui=ui_config)



@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png', mimetype='image/png')


@app.route('/api/search')
def api_search():
    """Search users by name, location, or role across all roles."""
    query = request.args.get('q', '').strip().lower()
    
    if not query or len(query) < 1:
        return jsonify({'success': True, 'users': []})
    
    import templates.account.db as db
    conn = db.get_db()
    cursor = conn.cursor()
    
    # Search across all users by username, location, title, or role
    cursor.execute('''
        SELECT id, username, location, profile_image, title, role
        FROM users
        WHERE LOWER(username) LIKE ?
           OR LOWER(location) LIKE ?
           OR LOWER(COALESCE(title, '')) LIKE ?
           OR LOWER(role) LIKE ?
        ORDER BY username ASC
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    
    users = []
    for row in cursor.fetchall():
        users.append({
            'id': row['id'],
            'username': row['username'],
            'location': row['location'] or '',
            'profile_image': row['profile_image'] or '',
            'title': row['title'] or '',
            'role': row['role'] or '',
        })
    
    conn.close()
    return jsonify({'success': True, 'users': users})


@app.route('/api/users-by-role')
def api_users_by_role():
    """Fetch users by role with their profile data for the home page sections."""
    role = request.args.get('role', '')
    limit = request.args.get('limit', 100, type=int)
    
    if not role:
        return jsonify({'success': False, 'error': 'Role parameter required'}), 400
    
    # Map role names to their equipment/price tables
    role_price_map = {
        'dj': ('dj_equipment', 'total_per_event'),
        'venue': ('venue_profiles', 'daily_rate'),
        'event': ('venue_profiles', 'daily_rate'),
        'photographer': ('photographer_profiles', 'daily_rate'),
        'tent': ('tent_profiles', 'daily_rate'),
        'tents': ('tent_profiles', 'daily_rate'),
        'caterer': ('caterer_profiles', 'daily_rate'),
    }
    
    table_name, price_column = role_price_map.get(role, (None, None))
    if not table_name:
        return jsonify({'success': False, 'error': 'Invalid role'}), 400

    import templates.account.db as db
    import templates.profile.profile as profile_module

    # Get users from curyent.db
    main_conn = db.get_db()
    main_cursor = main_conn.cursor()

    # Handle both 'event' and 'venue' roles, and both 'tents' and 'tent' roles
    role_conditions = []
    role_params = []
    if role in ('venue', 'event'):
        role_conditions.append("u.role IN ('venue', 'event')")
    elif role in ('tent', 'tents'):
        role_conditions.append("u.role IN ('tent', 'tents')")
    else:
        role_conditions.append("u.role = ?")
        role_params.append(role)

    role_where = ' AND '.join(role_conditions)
    main_cursor.execute(f'''
        SELECT id, username, location, profile_image, title
        FROM users u
        WHERE {role_where}
        ORDER BY u.created_at DESC
        LIMIT ?
    ''', role_params + [limit])
    users_rows = main_cursor.fetchall()
    main_conn.close()

    # Get prices from probase.db
    probase_conn = profile_module.get_probase_db()
    probase_cursor = probase_conn.cursor()

    users = []
    for row in users_rows:
        user_id = row['id']
        price = None
        try:
            probase_cursor.execute(f'SELECT {price_column} FROM {table_name} WHERE user_id = ?', (user_id,))
            price_row = probase_cursor.fetchone()
            if price_row:
                price = price_row[0]
        except Exception:
            pass

        users.append({
            'id': user_id,
            'username': row['username'],
            'location': row['location'] or '',
            'profile_image': row['profile_image'] or '',
            'title': row['title'] or '',
            'price': price,
        })

    probase_conn.close()
    return jsonify({'success': True, 'users': users})


def reset_all_databases():
    """Reset all databases to a clean state. Handles locked files gracefully."""
    import templates.account.db as main_db
    import templates.book.book as book_module
    import templates.profile.profile as profile_module
    import templates.chat.chat as chat_module
    import templates.notifications.noti as noti_module
    import glob
    import time

    # Retry logic for locked database files
    max_retries = 3
    retry_delay = 1

    def safe_reset(reset_func, name):
        """Try to reset a database with retries for locked files."""
        for attempt in range(max_retries):
            try:
                reset_func()
                return True, name
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False, name
            except Exception:
                return False, name

    results = []
    results.append(safe_reset(main_db.reset_db, "curyent.db"))
    results.append(safe_reset(book_module.reset_book_db, "booking.db"))
    results.append(safe_reset(profile_module.reset_probase_db, "probase.db"))
    results.append(safe_reset(chat_module.reset_db, "chatbase.db"))
    results.append(safe_reset(noti_module.reset_db, "notibase.db"))

    # Clear uploaded files
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    upload_files = glob.glob(os.path.join(upload_dir, '*'))
    for f in upload_files:
        try:
            os.remove(f)
        except OSError:
            pass

    # Ensure uploads directory exists for future uploads
    os.makedirs(upload_dir, exist_ok=True)

    # Return summary
    success = [name for ok, name in results if ok]
    failed = [name for ok, name in results if not ok]
    return success, failed


# =========================
# Payout Scheduler — pays provider 2 hours before event end time
# =========================

def check_and_process_event_payouts():
    """
    Background thread that runs every minute to check for bookings
    where the event end time is 2 hours away, and triggers B2C payout.
    """
    import time
    while True:
        try:
            import templates.book.book as book_module
            conn = book_module.get_book_db()
            cursor = conn.cursor()

            # Find bookings that:
            # 1. Are approved (service delivered)
            # 2. Have not been paid yet
            # 3. Have an event_end_date within the next 5 minutes of the 2-hour-before mark
            cursor.execute('''
                SELECT b.*, u.phone as provider_phone
                FROM bookings b
                LEFT JOIN users u ON b.booked_id = u.id
                WHERE b.approval_status = 'approved'
                  AND b.payout_status NOT IN ('paid', 'payout_failed')
                  AND b.event_end_date IS NOT NULL
            ''')
            bookings = cursor.fetchall()

            now = datetime.now()
            payout_window_start = timedelta(minutes=115)  # 1h55m before end (5-min window)
            payout_window_end = timedelta(minutes=120)     # 2h before end

            for booking in bookings:
                try:
                    event_end = datetime.fromisoformat(booking['event_end_date'])
                    time_until_end = event_end - now

                    # Check if we're in the payout window (2 hours before end, ±5 min)
                    if payout_window_start <= time_until_end <= payout_window_end:
                        print(f'[Payout Scheduler] Triggering payout for booking {booking["id"]} - '
                              f'event ends at {booking["event_end_date"]}')

                        # Initiate B2C payout
                        payout_success = False
                        if booking['provider_phone']:
                            import templates.book.mpesa as mpesa_module
                            mpesa_payout_result = mpesa_module.initiate_b2c_payout(
                                recipient_phone=booking['provider_phone'],
                                amount=booking['daily_rate'],
                                occasion=f'Service payout for {booking.get("celebration_title", "booking")}'
                            )
                            print(f'[Payout Scheduler] B2C result: {mpesa_payout_result}')
                            # Only mark as paid if the payout was actually initiated (not simulated)
                            payout_success = mpesa_payout_result.get('success', False) and not mpesa_payout_result.get('simulated', False)
                        else:
                            # No phone number — mark as failed
                            print(f'[Payout Scheduler] No provider phone for booking {booking["id"]}')

                        # Update payout status based on actual result
                        now_iso = now.isoformat()
                        if payout_success:
                            cursor.execute('''
                                UPDATE bookings SET payout_status = 'paid', payout_at = ?
                                WHERE id = ?
                            ''', (now_iso, booking['id']))
                        else:
                            # Mark as pending retry for simulated/failed payouts
                            cursor.execute('''
                                UPDATE bookings SET payout_status = 'pending_retry'
                                WHERE id = ? AND payout_status = 'scheduled_for_event'
                            ''', (booking['id'],))
                        conn.commit()

                        # Send notification
                        try:
                            import templates.notifications.noti as noti_module
                            if payout_success:
                                noti_module.create_notification(
                                    user_id=booking['booked_id'],
                                    title='Payout processed',
                                    message=f'You have been paid KES {booking["daily_rate"]:.0f} for '
                                            f'{booking.get("celebration_title", "the event")}.',
                                    notification_type='payout',
                                    related_item_id=booking['id'],
                                    priority='medium'
                                )
                            else:
                                noti_module.create_notification(
                                    user_id=booking['booked_id'],
                                    title='Payout pending',
                                    message=f'Your payout of KES {booking["daily_rate"]:.0f} for '
                                            f'{booking.get("celebration_title", "the event")} is being processed.',
                                    notification_type='payment_pending',
                                    related_item_id=booking['id'],
                                    priority='low'
                                )
                        except Exception:
                            pass

                except Exception as e:
                    print(f'[Payout Scheduler] Error processing booking: {e}')

            conn.close()

        except Exception as e:
            print(f'[Payout Scheduler] Error in payout check cycle: {e}')

        # Wait 60 seconds before next check
        time.sleep(60)


def start_payout_scheduler():
    """Start the payout scheduler as a background daemon thread."""
    import threading
    scheduler_thread = threading.Thread(
        target=check_and_process_event_payouts,
        daemon=True
    )
    scheduler_thread.start()
    print('[Payout Scheduler] Started — checking every minute for payouts 2 hours before event end')


def init_all_databases():
    """Initialize all databases. Called at startup for both development and production."""
    import templates.account.db as main_db
    main_db.init_db()

    import templates.book.book as book_module
    book_module.ensure_book_db_initialized()

    import templates.profile.profile as profile_module
    profile_module.ensure_probase_initialized()

    import templates.notifications.noti as noti_module
    noti_module.init_db()

    import templates.chat.chat as chat_module
    chat_module.init_db()

    import templates.admin.admin_db as admin_db
    admin_db.init_db()

    import templates.social.social as social_module
    social_module.init_social_db()


# Initialize databases at module level so Gunicorn can import and start the app
init_all_databases()


if __name__ == "__main__":
    start_payout_scheduler()
    # Use use_reloader=False to avoid database lock issues with Flask's debug reloader
    app.run(debug=True, use_reloader=False)
