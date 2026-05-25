# from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# from services.auth_service import AuthService

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
        
#         success, message = AuthService.login_user(username, password)
        
#         if success:
#             flash(message, 'success')
            
#             # Redirect based on user type
#             if session.get('user_type') == 'ngo':
#                 return redirect(url_for('ngo.dashboard'))
#             else:
#                 return redirect(url_for('individual.home'))
#         else:
#             flash(message, 'error')
#             return redirect(url_for('auth.login'))
    
#     return render_template('login.html')

# @auth_bp.route('/signup', methods=['POST'])
# def signup():
#     fullname = request.form.get('fullname')
#     username = request.form.get('username')
#     email = request.form.get('email')
#     password = request.form.get('password')
#     user_type = request.form.get('user_type', 'individual')
    
#     success, message = AuthService.register_user(
#         fullname, username, email, password, user_type
#     )
    
#     if success:
#         flash('Registration successful! Please login.', 'success')
#         return redirect(url_for('auth.login'))
#     else:
#         flash(message, 'error')
#         return redirect(url_for('auth.login'))

# @auth_bp.route('/logout')
# def logout():
#     AuthService.logout_user()
#     flash('Logged out successfully', 'success')
#     return redirect(url_for('auth.login'))




# V2
# from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# from services.auth_service import AuthService

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         success, message = AuthService.login_user(username, password)
#         if success:
#             flash(message, 'success')
#             # Get user_type from session (now guaranteed to be set)
#             user_type = session.get('user_type')
#             print(f"Redirecting based on user_type: {user_type}")  # debug
#             if user_type == 'ngo':
#                 return redirect(url_for('ngo.dashboard'))
#             else:
#                 # Default to individual home (also handles case where user_type is None)
#                 return redirect(url_for('individual.home'))
#         else:
#             flash(message, 'error')
#             return redirect(url_for('auth.login'))
#     return render_template('login.html')

# @auth_bp.route('/signup', methods=['POST'])
# def signup():
#     fullname = request.form.get('fullname')
#     username = request.form.get('username')
#     email = request.form.get('email')
#     password = request.form.get('password')
#     user_type = request.form.get('user_type', 'individual')  # from form, default individual
#     success, message = AuthService.register_user(fullname, username, email, password, user_type)
#     if success:
#         flash('Registration successful!', 'success')
#         # After registration, session already contains user_type from AuthService
#         if session.get('user_type') == 'ngo':
#             return redirect(url_for('ngo.dashboard'))
#         else:
#             return redirect(url_for('individual.home'))
#     else:
#         flash(message, 'error')
#         return redirect(url_for('auth.login'))

# @auth_bp.route('/logout')
# def logout():
#     AuthService.logout_user()
#     flash('Logged out successfully', 'success')
#     return redirect(url_for('auth.login'))



# V3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from services.auth_service import AuthService
import traceback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Please enter both username/email and password', 'error')
            return redirect(url_for('auth.login'))
        
        success, message = AuthService.login_user(username, password)
        if success:
            flash(message, 'success')
            user_type = session.get('user_type')
            current_app.logger.info(f"User {username} logged in as {user_type}")
            if user_type == 'ngo':
                return redirect(url_for('ngo.dashboard'))
            else:
                return redirect(url_for('individual.home'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'individual')
        
        # Validate required fields
        if not all([fullname, username, email, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.login'))
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('auth.login'))
        
        # Validate user_type
        if user_type not in ('individual', 'ngo'):
            user_type = 'individual'
        
        # Register user
        success, message = AuthService.register_user(
            fullname, username, email, password, user_type
        )
        
        if success:
            flash(message, 'success')
            # After registration, session is already set in AuthService
            if session.get('user_type') == 'ngo':
                return redirect(url_for('ngo.dashboard'))
            else:
                return redirect(url_for('individual.home'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.login'))
    except Exception as e:
        current_app.logger.error(f"Signup error: {str(e)}\n{traceback.format_exc()}")
        flash('An internal error occurred. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    AuthService.logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

