import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from flask_login import LoginManager
from models.mongo_models import find_user_by_id, update_user, change_user_password
from services.auth_service import AuthService
from routes.auth import auth_bp
from routes.individual import individual_bp
from routes.ngo import ngo_bp
from routes.api import api_bp

def create_app():
    """Application factory pattern."""
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                template_folder='templates')
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize Flask-Login (no SQLAlchemy)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return find_user_by_id(user_id)

    # Register blueprints
    app.register_blueprint(auth_bp)          # /login, /signup, /logout
    app.register_blueprint(individual_bp)    # /home, /services, /resources, /community, /about
    app.register_blueprint(ngo_bp)           # /ngo/dashboard, /ngo/analyze, /api/students
    app.register_blueprint(api_bp, url_prefix='/api')  # /api/upload, /api/tts, /api/voice/speak, etc.

    # Root route (landing page)
    @app.route('/')
    def index():
        return render_template('abcd.html')

    # ---------- Profile routes (added here for simplicity) ----------
    @app.route('/profile')
    def profile():
        if 'user_id' not in session:
            flash('Please login to view your profile', 'error')
            return redirect(url_for('auth.login'))
        user = find_user_by_id(session['user_id'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
        return render_template('profile.html', user=user)

    @app.route('/update_profile', methods=['POST'])
    def update_profile():
        if 'user_id' not in session:
            flash('Please login', 'error')
            return redirect(url_for('auth.login'))
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        if not fullname or not email:
            flash('All fields are required', 'error')
            return redirect(url_for('profile'))
        success = update_user(session['user_id'], fullname, email)
        if success:
            # Update session data
            session['fullname'] = fullname
            session['email'] = email
            flash('Profile updated successfully!', 'success')
        else:
            flash('Email already exists or update failed', 'error')
        return redirect(url_for('profile'))

    @app.route('/change_password', methods=['POST'])
    def change_password():
        if 'user_id' not in session:
            flash('Please login', 'error')
            return redirect(url_for('auth.login'))
        current = request.form.get('current_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        if not current or not new or not confirm:
            flash('All password fields are required', 'error')
            return redirect(url_for('profile'))
        if new != confirm:
            flash('New passwords do not match', 'error')
            return redirect(url_for('profile'))
        if len(new) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('profile'))
        success, msg = change_user_password(session['user_id'], current, new)
        flash(msg, 'success' if success else 'error')
        return redirect(url_for('profile'))

    return app

if __name__ == '__main__':
    app = create_app()
    # Disable the Werkzeug reloader on Windows to avoid intermittent socket errors
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)