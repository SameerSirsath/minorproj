# from flask import session
# from flask_login import login_user, logout_user
# from models.mongo_models import create_user, find_user_by_username_or_email, find_user_by_id
# from utils.validators import validate_user_input
# import bcrypt

# class AuthService:
#     @staticmethod
#     def register_user(fullname, username, email, password, user_type='individual'):
#         validation_error = validate_user_input({
#             'fullname': fullname, 'username': username, 'email': email, 'password': password
#         })
#         if validation_error:
#             return False, validation_error
        
#         existing = find_user_by_username_or_email(username)
#         if existing:
#             return False, 'Username already exists'
#         existing_email = find_user_by_username_or_email(email)
#         if existing_email:
#             return False, 'Email already exists'
        
#         user = create_user(fullname, username, email, password, user_type)
#         login_user(user)
#         session['user_id'] = user.id
#         session['username'] = user.username
#         session['fullname'] = user.full_name
#         session['user_type'] = user.user_type
#         session['email'] = user.email
#         return True, 'Registration successful'
    
#     @staticmethod
#     def login_user(username, password):
#         user = find_user_by_username_or_email(username)
#         if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
#             login_user(user)
#             session['user_id'] = user.id
#             session['username'] = user.username
#             session['fullname'] = user.full_name
#             session['user_type'] = user.user_type
#             session['email'] = user.email
#             return True, 'Login successful'
#         return False, 'Invalid username or password'
    
#     @staticmethod
#     def logout_user():
#         logout_user()
#         session.clear()
#         return True, 'Logged out successfully'


from flask import session
from flask_login import login_user, logout_user
from models.mongo_models import create_user, find_user_by_username_or_email
from utils.validators import validate_user_input
import bcrypt

class AuthService:
    @staticmethod
    def register_user(fullname, username, email, password, user_type='individual'):
        validation_error = validate_user_input({
            'fullname': fullname, 'username': username, 'email': email, 'password': password
        })
        if validation_error:
            return False, validation_error
        
        if find_user_by_username_or_email(username):
            return False, 'Username already exists'
        if find_user_by_username_or_email(email):
            return False, 'Email already exists'
        
        user = create_user(fullname, username, email, password, user_type)
        login_user(user)
        # Explicitly set session variables
        session['user_id'] = user.id
        session['username'] = user.username
        session['fullname'] = user.full_name
        session['user_type'] = user.user_type   # 'individual' or 'ngo'
        session['email'] = user.email
        return True, 'Registration successful'
    
    @staticmethod
    def login_user(username, password):
        user = find_user_by_username_or_email(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            # Explicitly set session variables from the database user object
            session['user_id'] = user.id
            session['username'] = user.username
            session['fullname'] = user.full_name
            session['user_type'] = user.user_type   # critical fix
            session['email'] = user.email
            # Optional: print to console for debugging
            print(f"Logged in as: {user.username}, user_type = {user.user_type}")
            return True, 'Login successful'
        return False, 'Invalid username or password'
    
    @staticmethod
    def logout_user():
        logout_user()
        session.clear()
        return True, 'Logged out successfully'