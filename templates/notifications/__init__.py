from flask import Blueprint, render_template, session
import templates.notifications.noti as noti_module

notifications_bp = Blueprint('notifications', __name__)

# Database initialization moved to app startup (curyent.py) to avoid import-time locks

# Register the notifications API blueprint
notifications_bp.register_blueprint(noti_module.noti_api_bp)


@notifications_bp.route('/notifications')
def notifications_page():
    """Render the notifications page."""
    user_id = session.get('user_id')
    username = session.get('username', 'User')
    logged_in = user_id is not None
    return render_template('notifications/notifications.html', user_id=user_id, username=username, logged_in=logged_in)
