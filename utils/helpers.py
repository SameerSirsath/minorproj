from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def ngo_required(f):
    """Decorator to require NGO user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'ngo':
            flash('NGO access required', 'error')
            return redirect(url_for('individual.home'))
        return f(*args, **kwargs)
    return decorated_function

def individual_required(f):
    """Decorator to require individual user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'individual':
            flash('Individual access required', 'error')
            return redirect(url_for('ngo.dashboard'))
        return f(*args, **kwargs)
    return decorated_function