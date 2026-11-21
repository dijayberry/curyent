from flask import Blueprint, render_template, session
import templates.chat.chat as chat_module

chat_bp = Blueprint('chat', __name__)

# Database initialization moved to app startup (curyent.py) to avoid import-time locks

# Register the chat API blueprint
chat_bp.register_blueprint(chat_module.chat_api_bp)


@chat_bp.route('/chat')
def chat_page():
    """Render the chat page."""
    user_id = session.get('user_id')
    username = session.get('username', 'User')
    logged_in = user_id is not None
    return render_template('chat/chat.html', user_id=user_id, username=username, logged_in=logged_in)
