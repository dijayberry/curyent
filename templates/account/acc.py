from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import re
import templates.account.db as db
import templates.account.whatsapp as whatsapp

account_bp = Blueprint('account', __name__)


def normalize_phone(phone):
    """Normalize phone number to +2547xxxxxxxx format by auto-adding +254 prefix if missing."""
    if not phone:
        return None, 'Phone number is required'
    # Remove any spaces, dashes, or parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # If it already starts with +254, validate the full format
    if cleaned.startswith('+254'):
        pattern = r'^\+2547\d{8}$'
        if re.match(pattern, cleaned):
            return cleaned, 'Valid'
        return None, 'Phone number must be in format +2547xxxxxxxx (e.g., +254712345678)'
    # If it starts with 07, replace with +2547
    if cleaned.startswith('07'):
        cleaned = '+254' + cleaned[1:]
    # If it starts with 7 followed by 8 digits, prepend +254
    elif cleaned.startswith('7') and len(cleaned) == 9:
        cleaned = '+254' + cleaned
    # If it's 10 digits starting with 7, prepend +254
    elif len(cleaned) == 10 and cleaned[0] == '7':
        cleaned = '+254' + cleaned
    else:
        return None, 'Phone number must start with 7 (e.g., 712345678)'
    # Final validation
    pattern = r'^\+2547\d{8}$'
    if re.match(pattern, cleaned):
        return cleaned, 'Valid'
    return None, 'Phone number must be in format +2547xxxxxxxx (e.g., +254712345678)'

# Database initialization moved to app startup (curyent.py) to avoid import-time locks
# Call db.init_db() once at startup instead of on import

# Sync users table to other databases so JOIN queries work
def sync_all_dbs():
    """Sync users table to booking.db and probase.db after registration."""
    try:
        import templates.book.book as book_module
        book_module.sync_users_to_book_db()
    except Exception:
        pass
    try:
        import templates.profile.profile as profile_module
        profile_module.sync_users_to_probase_db()
    except Exception:
        pass


@account_bp.route('/account/client', methods=['GET', 'POST'])
def client():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()

        # Normalize phone number to +2547xxxxxxxx format
        normalized_phone, phone_msg = normalize_phone(phone)
        if normalized_phone is None:
            return render_template('account/client.html', error=phone_msg)
        phone = normalized_phone

        # Handle profile picture upload
        profile_image = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and file.filename != '':
                allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in allowed:
                    import os
                    import uuid
                    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    filename = f"{uuid.uuid4().hex}.{ext}"
                    file.save(os.path.join(upload_dir, filename))
                    profile_image = f"/static/uploads/{filename}"

        # Check if username or email already exists
        if db.username_exists(username):
            return render_template('account/client.html', error='Username already exists')
        if db.email_exists(email):
            return render_template('account/client.html', error='Email already registered')

        # Register user as client (no title for clients)
        user_id = db.register_user(username, email, password, 'client', phone, location, profile_image, title=None)

        if user_id is None:
            return render_template('account/client.html', error='Failed to register user')

        # Sync users to other databases
        sync_all_dbs()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['username'] = username

        # Redirect clients to home page (not profile)
        return redirect(url_for('home'))

    return render_template('account/client.html')


@account_bp.route('/account/djs', methods=['GET', 'POST'])
def djs():
    if request.method == 'POST':
        # Collect form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        national_id = request.form.get('national_id', '').strip()
        daily_rate = float(request.form.get('daily_rate', '0'))
        
        # Normalize phone number to +2547xxxxxxxx format
        normalized_phone, phone_msg = normalize_phone(phone)
        if normalized_phone is None:
            return jsonify({'success': False, 'message': phone_msg}), 400
        phone = normalized_phone
        
        # Calculate equipment value from checked equipment items
        equipment_prices = {
            'equipment_pc': 700,
            'equipment_controller': 800,
            'equipment_mixer': 3000,
            'equipment_speakers': 3000,
            'equipment_generator': 2000,
            'equipment_projector': 2000,
            'equipment_microphones': 1500,
            'equipment_instruments': 2000,
        }
        equipment_value = 0
        for equip_key, price in equipment_prices.items():
            if request.form.get(equip_key) == 'on':
                equipment_value += price
        
        # Total per event = Daily Rate + Equipment value
        total_per_event = daily_rate + equipment_value
        
        # Collect equipment model details
        pc_model = request.form.get('pc_model', '').strip()
        controller_model = request.form.get('controller_model', '').strip()
        mixer_model = request.form.get('mixer_model', '').strip()
        speakers_model = request.form.get('speakers_model', '').strip()
        speakers_quantity = request.form.get('speakers_quantity', '').strip()
        generator_model = request.form.get('generator_model', '').strip()
        generator_power = request.form.get('generator_power', '').strip()
        projector_model = request.form.get('projector_model', '').strip()
        microphones_model = request.form.get('microphones_model', '').strip()
        microphones_quantity = request.form.get('microphones_quantity', '').strip()
        instruments_name = request.form.get('instruments_name', '').strip()
        instruments_quantity = request.form.get('instruments_quantity', '').strip()
        
        # Handle file uploads (profile picture and verification images)
        import os
        import uuid

        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        def save_uploaded_file(file_key, allow_multiple=False):
            """Save uploaded file(s) and return path(s)."""
            if file_key not in request.files:
                return None if not allow_multiple else []
            
            if allow_multiple:
                files = request.files.getlist(file_key)
                paths = []
                for file in files:
                    if file and file.filename and file.filename != '':
                        allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                        if ext in allowed:
                            filename = f"{uuid.uuid4().hex}.{ext}"
                            file.save(os.path.join(upload_dir, filename))
                            paths.append(f"/static/uploads/{filename}")
                return paths if paths else []
            else:
                file = request.files[file_key]
                if file and file.filename and file.filename != '':
                    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    if ext in allowed:
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        file.save(os.path.join(upload_dir, filename))
                        return f"/static/uploads/{filename}"
                return None

        # Handle profile picture upload
        profile_image = save_uploaded_file('profile_picture')
        
        # Handle verification image uploads
        mixer_image = save_uploaded_file('mixer_image')
        speakers_image = save_uploaded_file('speakers_image', allow_multiple=True)
        generator_image = save_uploaded_file('generator_image')
        microphones_image = save_uploaded_file('microphones_image', allow_multiple=True)
        instruments_image = save_uploaded_file('instruments_image', allow_multiple=True)
        
        # Check if username or email already exists
        if db.username_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if db.email_exists(email):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Register user with profile image and title
        user_id = db.register_user(username, email, password, 'dj', phone, location, profile_image, title='DJ')
        
        if user_id is None:
            return jsonify({'success': False, 'message': 'Failed to register user'}), 500
        
        # Save DJ equipment data - total_per_event = daily_rate + equipment_value
        conn = db.get_db()
        cursor = conn.cursor()
        
        # Convert numeric fields safely
        speakers_qty = int(speakers_quantity) if speakers_quantity else None
        generator_pwr = float(generator_power) if generator_power else None
        microphones_qty = int(microphones_quantity) if microphones_quantity else None
        instruments_qty = int(instruments_quantity) if instruments_quantity else None
        
        # Convert lists to JSON strings for storage
        import json
        speakers_image_str = json.dumps(speakers_image) if speakers_image else None
        microphones_image_str = json.dumps(microphones_image) if microphones_image else None
        instruments_image_str = json.dumps(instruments_image) if instruments_image else None
        
        cursor.execute('''
            INSERT INTO dj_equipment (
                user_id, total_per_event, national_id,
                pc_model, controller_model, mixer_model,
                speakers_model, speakers_quantity,
                generator_model, generator_power,
                projector_model,
                microphones_model, microphones_quantity,
                instruments_name, instruments_quantity,
                mixer_image, speakers_image, generator_image, microphones_image, instruments_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, float(total_per_event), national_id,
            pc_model, controller_model, mixer_model,
            speakers_model, speakers_qty,
            generator_model, generator_pwr,
            projector_model,
            microphones_model, microphones_qty,
            instruments_name, instruments_qty,
            mixer_image, speakers_image_str, generator_image, microphones_image_str, instruments_image_str
        ))
        conn.commit()
        conn.close()
        
        # Sync users to other databases
        sync_all_dbs()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'message': 'DJ account created successfully', 'user_id': user_id, 'redirect': '/profile'})
    
    return render_template('account/djs.html')


@account_bp.route('/account/venue', methods=['GET', 'POST'])
def venue():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        national_id = request.form.get('national_id', '').strip()
        daily_rate = request.form.get('daily_rate', '0')
        
        # Normalize phone number to +2547xxxxxxxx format
        normalized_phone, phone_msg = normalize_phone(phone)
        if normalized_phone is None:
            return jsonify({'success': False, 'message': phone_msg}), 400
        phone = normalized_phone
        
        if db.username_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if db.email_exists(email):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        user_id = db.register_user(username, email, password, 'venue', phone, location, title='Venue Owner')
        
        if user_id is None:
            return jsonify({'success': False, 'message': 'Failed to register user'}), 500
        
        # Collect amenities
        amenities = []
        for key in request.form:
            if key.startswith('amenity_'):
                amenities.append(request.form[key])
        amenities_str = ','.join(amenities) if amenities else ''
        
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_venues (user_id, venue_name, venue_type, capacity, amenities, event_description, daily_rate, national_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, request.form.get('venue_name', ''), request.form.get('venue_type', ''),
              int(request.form.get('capacity', 0)), amenities_str,
              request.form.get('event_description', ''), float(daily_rate), national_id))
        conn.commit()
        conn.close()

        # Sync users to other databases
        sync_all_dbs()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'message': 'Venue account created successfully', 'user_id': user_id, 'redirect': '/profile'})
    
    return render_template('account/venue.html')


@account_bp.route('/account/photographer', methods=['GET', 'POST'])
def photographer():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        national_id = request.form.get('national_id', '').strip()
        daily_rate = request.form.get('daily_rate', '0')
        
        # Normalize phone number to +2547xxxxxxxx format
        normalized_phone, phone_msg = normalize_phone(phone)
        if normalized_phone is None:
            return jsonify({'success': False, 'message': phone_msg}), 400
        phone = normalized_phone
        
        if db.username_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if db.email_exists(email):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        user_id = db.register_user(username, email, password, 'photographer', phone, location, title='Photographer')
        
        if user_id is None:
            return jsonify({'success': False, 'message': 'Failed to register user'}), 500
        
        # Collect services
        services = []
        for key in request.form:
            if key.startswith('service_'):
                services.append(request.form[key])
        services_str = ','.join(services) if services else ''
        
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO photographer_profiles (user_id, business_name, specialization, experience, camera_equipment, services, photographer_description, daily_rate, national_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, request.form.get('business_name', ''), request.form.get('specialization', ''),
              int(request.form.get('experience', 0)), request.form.get('camera_equipment', ''),
              services_str, request.form.get('photographer_description', ''), float(daily_rate), national_id))
        conn.commit()
        conn.close()

        # Sync users to other databases
        sync_all_dbs()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'message': 'Photographer account created successfully', 'user_id': user_id, 'redirect': '/profile'})
    
    return render_template('account/photographer.html')


@account_bp.route('/account/tents', methods=['GET', 'POST'])
def tents():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        national_id = request.form.get('national_id', '').strip()
        daily_rate = request.form.get('daily_rate', '0')
        
        # Normalize phone number to +2547xxxxxxxx format
        normalized_phone, phone_msg = normalize_phone(phone)
        if normalized_phone is None:
            return jsonify({'success': False, 'message': phone_msg}), 400
        phone = normalized_phone
        
        if db.username_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if db.email_exists(email):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        user_id = db.register_user(username, email, password, 'tent', phone, location, title='Tent Rental')
        
        if user_id is None:
            return jsonify({'success': False, 'message': 'Failed to register user'}), 500
        
        # Collect tent types
        tent_types = []
        for key in request.form:
            if key.startswith('tent_type_'):
                tent_types.append(request.form[key])
        tent_types_str = ','.join(tent_types) if tent_types else ''
        
        # Collect additional equipment
        equipment = []
        for key in request.form:
            if key.startswith('equipment_'):
                equipment.append(request.form[key])
        equipment_str = ','.join(equipment) if equipment else ''
        
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tent_inventory (user_id, business_name, tent_types, tent_sizes, total_tents, additional_equipment, delivery, delivery_areas, tent_description, daily_rate, national_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, request.form.get('business_name', ''), tent_types_str,
              request.form.get('tent_sizes', ''), int(request.form.get('total_tents', 0)),
              equipment_str, request.form.get('delivery', ''), request.form.get('delivery_areas', ''),
              request.form.get('tent_description', ''), float(daily_rate), national_id))
        conn.commit()
        conn.close()

        # Sync users to other databases
        sync_all_dbs()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'message': 'Tent account created successfully', 'user_id': user_id, 'redirect': '/profile'})
    
    return render_template('account/tents.html')


@account_bp.route('/account/caterer', methods=['GET', 'POST'])
def caterer():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        national_id = request.form.get('national_id', '').strip()
        daily_rate = request.form.get('daily_rate', '0')
        
        # Normalize phone number to +2547xxxxxxxx format
        normalized_phone, phone_msg = normalize_phone(phone)
        if normalized_phone is None:
            return jsonify({'success': False, 'message': phone_msg}), 400
        phone = normalized_phone
        
        if db.username_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if db.email_exists(email):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        user_id = db.register_user(username, email, password, 'caterer', phone, location, title='Caterer')
        
        if user_id is None:
            return jsonify({'success': False, 'message': 'Failed to register user'}), 500
        
        # Collect services
        services = []
        for key in request.form:
            if key.startswith('service_'):
                services.append(request.form[key])
        services_str = ','.join(services) if services else ''
        
        # Collect dietary options
        dietary = []
        for key in request.form:
            if key.startswith('dietary_'):
                dietary.append(request.form[key])
        dietary_str = ','.join(dietary) if dietary else ''
        
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO caterer_profiles (user_id, business_name, cuisine_type, per_person_rate, max_guests, min_guests, menu_items, services, dietary_options, caterer_description, daily_rate, national_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, request.form.get('business_name', ''), request.form.get('cuisine_type', ''),
              float(request.form.get('per_person_rate', 0)), int(request.form.get('max_guests', 0)),
              int(request.form.get('min_guests', 0)), request.form.get('menu_items', ''),
              services_str, dietary_str, request.form.get('caterer_description', ''),
              float(daily_rate), national_id))
        conn.commit()
        conn.close()

        # Sync users to other databases
        sync_all_dbs()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'message': 'Caterer account created successfully', 'user_id': user_id, 'redirect': '/profile'})
    
    return render_template('account/caterer.html')


@account_bp.route('/account/logi', methods=['GET', 'POST'])
def logi():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Check if email exists in database
        if not db.email_exists(email):
            # Email not found, redirect to role selection page for registration
            return redirect(url_for('account.about'))
        
        # Authenticate user
        user = db.login_user(email, password)
        if user:
            # Sync users to other databases
            sync_all_dbs()

            # Set session and redirect to home page
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            # Email exists but password is wrong
            return render_template('account/logi.html', error='Invalid password')
    
    return render_template('account/logi.html')


@account_bp.route('/otp')
def otp():
    phone = request.args.get('phone', '')
    is_register = request.args.get('register', '0')
    is_forgot = request.args.get('forgot', '0')
    return render_template('account/otp.html', phone=phone, is_register=is_register, is_forgot=is_forgot)


# =========================
# API: Prepare OTP for Registration
# =========================

@account_bp.route('/api/prepare-otp', methods=['POST'])
def prepare_otp():
    """Validate phone, send OTP, and store verification flag in session for registration flow."""
    data = request.get_json()
    phone = data.get('phone', '').strip()

    if not phone:
        return jsonify({'success': False, 'message': 'Phone number is required'}), 400

    # Normalize phone number
    normalized, msg = normalize_phone(phone)
    if normalized is None:
        return jsonify({'success': False, 'message': msg}), 400

    # Generate and send OTP
    otp_code = whatsapp.generate_otp()
    db.save_otp_code(normalized, otp_code)
    result = whatsapp.send_whatsapp_otp(normalized, otp_code)

    # Store phone in session for registration flow
    session['otp_phone'] = normalized
    session['otp_verified'] = False

    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'phone': normalized
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to send OTP'
        }), 500


# =========================
# API: Complete Registration After OTP
# =========================

@account_bp.route('/api/complete-registration', methods=['POST'])
def complete_registration():
    """After OTP is verified, retrieve stored form data and complete registration."""
    import json as json_mod

    # Check OTP verification
    if not session.get('otp_verified'):
        return jsonify({'success': False, 'message': 'Phone not verified'}), 400

    # Get stored form data from sessionStorage (sent as JSON)
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No registration data'}), 400

    action = data.get('_action', '')
    phone = session.get('otp_phone', '')

    # Handle profile picture from form data (base64 or skip)
    profile_image = None
    # Note: profile pictures need to be handled separately via file upload
    # For now, registration without picture works

    # Determine role from action URL
    role = 'client'
    if '/djs' in action:
        role = 'dj'
    elif '/venue' in action:
        role = 'venue'
    elif '/photographer' in action:
        role = 'photographer'
    elif '/tents' in action:
        role = 'tent'
    elif '/caterer' in action:
        role = 'caterer'

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    location = data.get('location', '').strip()

    # Check if username or email already exists
    if db.username_exists(username):
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    if db.email_exists(email):
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    # Title mapping
    title_map = {
        'dj': 'DJ',
        'venue': 'Venue Owner',
        'photographer': 'Photographer',
        'tent': 'Tent Rental',
        'caterer': 'Caterer',
        'client': None
    }

    # Register user
    user_id = db.register_user(username, email, password, role, phone, location, profile_image, title=title_map.get(role))

    if user_id is None:
        return jsonify({'success': False, 'message': 'Failed to register user'}), 500

    # Save role-specific data
    try:
        if role == 'dj':
            conn = db.get_db()
            cursor = conn.cursor()
            daily_rate = float(data.get('daily_rate', '0'))
            equipment_prices = {
                'equipment_pc': 700, 'equipment_controller': 800, 'equipment_mixer': 3000,
                'equipment_speakers': 3000, 'equipment_generator': 2000, 'equipment_projector': 2000,
                'equipment_microphones': 1500, 'equipment_instruments': 2000,
            }
            equipment_value = 0
            for equip_key, price in equipment_prices.items():
                if data.get(equip_key) == 'on':
                    equipment_value += price
            total_per_event = daily_rate + equipment_value
            national_id = data.get('national_id', '').strip()
            cursor.execute('''
                INSERT INTO dj_equipment (
                    user_id, total_per_event, national_id,
                    pc_model, controller_model, mixer_model,
                    speakers_model, speakers_quantity,
                    generator_model, generator_power,
                    projector_model,
                    microphones_model, microphones_quantity,
                    instruments_name, instruments_quantity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, float(total_per_event), national_id,
                data.get('pc_model', ''), data.get('controller_model', ''), data.get('mixer_model', ''),
                data.get('speakers_model', ''), int(data.get('speakers_quantity', 0) or 0),
                data.get('generator_model', ''), float(data.get('generator_power', 0) or 0),
                data.get('projector_model', ''),
                data.get('microphones_model', ''), int(data.get('microphones_quantity', 0) or 0),
                data.get('instruments_name', ''), int(data.get('instruments_quantity', 0) or 0)
            ))
            conn.commit()
            conn.close()

        elif role == 'venue':
            conn = db.get_db()
            cursor = conn.cursor()
            amenities = [v for k, v in data.items() if k.startswith('amenity_') and v]
            amenities_str = ','.join(amenities)
            cursor.execute('''
                INSERT INTO event_venues (user_id, venue_name, venue_type, capacity, amenities, event_description, daily_rate, national_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, data.get('venue_name', ''), data.get('venue_type', ''),
                  int(data.get('capacity', 0) or 0), amenities_str,
                  data.get('event_description', ''), float(data.get('daily_rate', 0) or 0),
                  data.get('national_id', '')))
            conn.commit()
            conn.close()

        elif role == 'photographer':
            conn = db.get_db()
            cursor = conn.cursor()
            services = [v for k, v in data.items() if k.startswith('service_') and v]
            services_str = ','.join(services)
            cursor.execute('''
                INSERT INTO photographer_profiles (user_id, business_name, specialization, experience, camera_equipment, services, photographer_description, daily_rate, national_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, data.get('business_name', ''), data.get('specialization', ''),
                  int(data.get('experience', 0) or 0), data.get('camera_equipment', ''),
                  services_str, data.get('photographer_description', ''),
                  float(data.get('daily_rate', 0) or 0), data.get('national_id', '')))
            conn.commit()
            conn.close()

        elif role == 'tent':
            conn = db.get_db()
            cursor = conn.cursor()
            tent_types = [v for k, v in data.items() if k.startswith('tent_type_') and v]
            tent_types_str = ','.join(tent_types)
            equipment = [v for k, v in data.items() if k.startswith('equipment_') and v]
            equipment_str = ','.join(equipment)
            cursor.execute('''
                INSERT INTO tent_inventory (user_id, business_name, tent_types, tent_sizes, total_tents, additional_equipment, delivery, delivery_areas, tent_description, daily_rate, national_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, data.get('business_name', ''), tent_types_str,
                  data.get('tent_sizes', ''), int(data.get('total_tents', 0) or 0),
                  equipment_str, data.get('delivery', ''), data.get('delivery_areas', ''),
                  data.get('tent_description', ''), float(data.get('daily_rate', 0) or 0),
                  data.get('national_id', '')))
            conn.commit()
            conn.close()

        elif role == 'caterer':
            conn = db.get_db()
            cursor = conn.cursor()
            services = [v for k, v in data.items() if k.startswith('service_') and v]
            services_str = ','.join(services)
            dietary = [v for k, v in data.items() if k.startswith('dietary_') and v]
            dietary_str = ','.join(dietary)
            cursor.execute('''
                INSERT INTO caterer_profiles (user_id, business_name, cuisine_type, per_person_rate, max_guests, min_guests, menu_items, services, dietary_options, caterer_description, daily_rate, national_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, data.get('business_name', ''), data.get('cuisine_type', ''),
                  float(data.get('per_person_rate', 0) or 0), int(data.get('max_guests', 0) or 0),
                  int(data.get('min_guests', 0) or 0), data.get('menu_items', ''),
                  services_str, dietary_str, data.get('caterer_description', ''),
                  float(data.get('daily_rate', 0) or 0), data.get('national_id', '')))
            conn.commit()
            conn.close()

    except Exception as e:
        print(f'[Registration Error] {str(e)}')
        return jsonify({'success': False, 'message': f'Failed to save {role} data'}), 500

    # Sync users to other databases
    sync_all_dbs()

    # Auto-login
    session['user_id'] = user_id
    session['username'] = username
    session['otp_verified'] = True

    # Determine redirect
    redirect_url = '/profile'
    if role == 'client':
        redirect_url = url_for('home')

    return jsonify({
        'success': True,
        'message': f'{role.title()} account created successfully',
        'user_id': user_id,
        'redirect': redirect_url
    })


@account_bp.route('/role')
def about():
    return render_template('home/role.html')


# =========================
# API: Check Username Availability
# =========================

@account_bp.route('/api/check-username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'}), 400
    
    exists = db.username_exists(username)
    return jsonify({'available': not exists, 'message': 'Username already exists' if exists else 'Username is available'})


# =========================
# API: Check Email Availability
# =========================

@account_bp.route('/api/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'}), 400
    
    exists = db.email_exists(email)
    if exists:
        return jsonify({'available': False, 'message': 'Email already registered', 'redirect': '/account/logi'})
    return jsonify({'available': True, 'message': 'Email is available'})


# =========================
# API: Forgot Password (Email-based)
# =========================

@account_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Handle forgot password flow: look up email, find phone, send OTP.
    If email doesn't exist, return a redirect to the role registration page."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    # Look up user by email
    user = db.get_user_by_email(email)

    if user is None:
        # Email not found — direct to registration
        return jsonify({
            'success': False,
            'emailExists': False,
            'message': 'No account found with this email. Please create an account.',
            'redirect': '/role'
        }), 404

    # Check if user has a phone number
    phone = user['phone']
    if not phone:
        return jsonify({
            'success': False,
            'emailExists': True,
            'message': 'No phone number registered for this email. Please contact support.'
        }), 400

    # Generate and send OTP to the user's phone
    otp_code = whatsapp.generate_otp()
    db.save_otp_code(phone, otp_code)
    result = whatsapp.send_whatsapp_otp(phone, otp_code)

    if result['success']:
        return jsonify({
            'success': True,
            'emailExists': True,
            'message': 'OTP sent to your registered phone number',
            'phone': phone
        })
    else:
        # WhatsApp send failed, but OTP is still saved in DB
        # Return success so the user can proceed to the OTP verification page
        # and retry sending the OTP from there
        print(f'[Forgot Password] WhatsApp send failed for {phone}, but OTP is saved in DB')
        return jsonify({
            'success': True,
            'emailExists': True,
            'message': 'OTP generation failed. Please try sending again, or contact support.',
            'phone': phone,
            'otpSent': False
        })


# =========================
# API: Send OTP via WhatsApp
# =========================

@account_bp.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone', '').strip()

    if not phone:
        return jsonify({'success': False, 'message': 'Phone number is required'}), 400

    # Normalize phone number using the same function as prepare-otp
    normalized, msg = normalize_phone(phone)
    if normalized is None:
        return jsonify({'success': False, 'message': msg}), 400
    phone = normalized

    # Generate OTP code
    otp_code = whatsapp.generate_otp()

    # Save to database
    db.save_otp_code(phone, otp_code)

    # Send via WhatsApp
    result = whatsapp.send_whatsapp_otp(phone, otp_code)

    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'phone': phone
        })
    else:
        # WhatsApp send failed, but OTP is still saved in DB
        print(f'[Send OTP] WhatsApp send failed for {phone}, but OTP is saved in DB')
        return jsonify({
            'success': True,
            'message': 'OTP saved but WhatsApp delivery failed. Please try sending again.',
            'phone': phone,
            'otpSent': False
        })


# =========================
# API: Verify OTP Code
# =========================

@account_bp.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    otp_code = data.get('otp_code', '').strip()

    if not phone or not otp_code:
        return jsonify({'success': False, 'message': 'Phone number and OTP code are required'}), 400

    # Normalize phone number using the same function as prepare-otp
    normalized, msg = normalize_phone(phone)
    if normalized is None:
        return jsonify({'success': False, 'message': msg}), 400
    phone = normalized

    # Verify OTP
    if db.verify_otp(phone, otp_code):
        session['otp_verified'] = True
        session['otp_phone'] = phone
        return jsonify({'success': True, 'message': 'Phone number verified successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP code'}), 400


# =========================
# API: Reset Password
# =========================

@account_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset user password after OTP verification via forgot password flow."""
    data = request.get_json()
    phone = data.get('phone', '').strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not phone or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    # Validate password match
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

    # Validate password strength
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Normalize phone number
    normalized, msg = normalize_phone(phone)
    if normalized is None:
        return jsonify({'success': False, 'message': msg}), 400
    phone = normalized

    # Check OTP verification
    if not session.get('otp_verified'):
        return jsonify({'success': False, 'message': 'Phone not verified'}), 400

    # Find user by phone number
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE phone = ?', (phone,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'No account found with this phone number'}), 404

    # Hash and update password
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user['id']))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Password reset successfully'
    })


