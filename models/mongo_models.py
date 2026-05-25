# # models/mongo_models.py
# from bson import ObjectId
# from datetime import datetime
# import bcrypt
# from flask_login import UserMixin
# from mongo_config.mongo import users_collection, students_collection

# class MongoUser(UserMixin):
#     """Wrapper for MongoDB user document to work with Flask-Login."""
#     def __init__(self, user_dict):
#         self.id = str(user_dict['_id'])
#         self.username = user_dict['username']
#         self.full_name = user_dict.get('full_name', '')
#         self.email = user_dict.get('email', '')
#         self.user_type = user_dict.get('user_type', 'individual')
#         self.password_hash = user_dict.get('password_hash', '')
#         self.created_at = user_dict.get('created_at')

#     def get_id(self):
#         return self.id

# # -------------------- User Helpers --------------------
# def create_user(full_name, username, email, password, user_type='individual'):
#     """Create a new user with hashed password."""
#     hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#     user = {
#         'full_name': full_name,
#         'username': username,
#         'email': email,
#         'password_hash': hashed,
#         'user_type': user_type,
#         'created_at': datetime.utcnow()
#     }
#     result = users_collection.insert_one(user)
#     user['_id'] = result.inserted_id
#     return MongoUser(user)

# def find_user_by_username_or_email(identifier):
#     """Find user by username or email."""
#     user = users_collection.find_one({'$or': [{'username': identifier}, {'email': identifier}]})
#     return MongoUser(user) if user else None

# def find_user_by_id(user_id):
#     """Find user by ObjectId string."""
#     user = users_collection.find_one({'_id': ObjectId(user_id)})
#     return MongoUser(user) if user else None

# def update_user(user_id, full_name=None, email=None):
#     """Update user's full name and/or email."""
#     update_data = {}
#     if full_name:
#         update_data['full_name'] = full_name
#     if email:
#         update_data['email'] = email
#     if update_data:
#         users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
#         return True
#     return False

# # -------------------- Student Helpers (for NGOs) --------------------
# def get_all_students(ngo_id):
#     """Get all students belonging to a specific NGO (by ngo_id)."""
#     students = list(students_collection.find({'ngo_id': str(ngo_id)}))
#     # Convert ObjectId to string for JSON serialization
#     for s in students:
#         s['id'] = str(s['_id'])
#         del s['_id']
#     return students

# def add_student(ngo_id, name, age, certificate_file=None):
#     """Add a new student."""
#     student = {
#         'ngo_id': str(ngo_id),
#         'name': name,
#         'age': int(age) if age else None,
#         'certificate_file': certificate_file,
#         'disability_type': None,
#         'created_at': datetime.utcnow()
#     }
#     result = students_collection.insert_one(student)
#     student['_id'] = result.inserted_id
#     student['id'] = str(result.inserted_id)
#     del student['_id']
#     return student

# def update_student(student_id, ngo_id, name, age, certificate_file=None):
#     """Update student information. Returns True if successful."""
#     update_data = {'name': name, 'age': int(age) if age else None}
#     if certificate_file:
#         update_data['certificate_file'] = certificate_file
#     result = students_collection.update_one(
#         {'_id': ObjectId(student_id), 'ngo_id': str(ngo_id)},
#         {'$set': update_data}
#     )
#     return result.modified_count > 0

# def delete_student(student_id, ngo_id):
#     """Delete a student. Returns True if deleted."""
#     result = students_collection.delete_one({'_id': ObjectId(student_id), 'ngo_id': str(ngo_id)})
#     return result.deleted_count > 0
# models/mongo_models.py
from bson import ObjectId
from datetime import datetime
import bcrypt
from flask_login import UserMixin
from mongo_config.mongo import users_collection, students_collection

class MongoUser(UserMixin):
    """Wrapper for MongoDB user document to work with Flask-Login."""
    def __init__(self, user_dict):
        if not user_dict:
            # Handle case where no user found
            self.id = None
            self.username = ''
            self.full_name = ''
            self.email = ''
            self.user_type = 'individual'   # safe default
            self.password_hash = ''
            self.created_at = None
            return
        
        self.id = str(user_dict.get('_id', ''))
        self.username = user_dict.get('username', '')
        self.full_name = user_dict.get('full_name', '')
        self.email = user_dict.get('email', '')
        # Critical: ensure user_type is either 'individual' or 'ngo'
        self.user_type = user_dict.get('user_type', 'individual')
        if self.user_type not in ('individual', 'ngo'):
            self.user_type = 'individual'   # fallback for corrupted data
        self.password_hash = user_dict.get('password_hash', '')
        self.created_at = user_dict.get('created_at')

    def get_id(self):
        return self.id

    def is_ngo(self):
        return self.user_type == 'ngo'

    def is_individual(self):
        return self.user_type == 'individual'

# -------------------- User Helpers --------------------
def create_user(full_name, username, email, password, user_type='individual'):
    """Create a new user with hashed password.
    user_type must be 'individual' or 'ngo'."""
    if user_type not in ('individual', 'ngo'):
        raise ValueError("user_type must be 'individual' or 'ngo'")
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        'full_name': full_name,
        'username': username,
        'email': email,
        'password_hash': hashed,
        'user_type': user_type,
        'created_at': datetime.utcnow()
    }
    result = users_collection.insert_one(user)
    user['_id'] = result.inserted_id
    return MongoUser(user)

def find_user_by_username_or_email(identifier):
    """Find user by username or email. Returns MongoUser or None."""
    try:
        user = users_collection.find_one({'$or': [{'username': identifier}, {'email': identifier}]})
        return MongoUser(user) if user else None
    except Exception as e:
        print(f"Error finding user: {e}")
        return None

def find_user_by_id(user_id):
    """Find user by ObjectId string. Returns MongoUser or None."""
    try:
        if not ObjectId.is_valid(user_id):
            return None
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return MongoUser(user) if user else None
    except Exception as e:
        print(f"Error finding user by ID: {e}")
        return None

def update_user(user_id, full_name=None, email=None):
    """Update user's full name and/or email. Returns True if changed."""
    if not ObjectId.is_valid(user_id):
        return False
    update_data = {}
    if full_name:
        update_data['full_name'] = full_name
    if email:
        update_data['email'] = email
    if update_data:
        result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        return result.modified_count > 0
    return False

def get_user_type(user_id):
    """Quick helper to get user_type of a user by ID without loading full object."""
    user = users_collection.find_one({'_id': ObjectId(user_id)}, {'user_type': 1})
    return user.get('user_type', 'individual') if user else None

# -------------------- Student Helpers (for NGOs) --------------------
def get_all_students(ngo_id):
    """Get all students belonging to a specific NGO (by ngo_id)."""
    students = list(students_collection.find({'ngo_id': str(ngo_id)}))
    for s in students:
        s['id'] = str(s['_id'])
        del s['_id']
    return students

def add_student(ngo_id, name, age, certificate_file=None):
    """Add a new student. Returns the created student dict with 'id' field."""
    student = {
        'ngo_id': str(ngo_id),
        'name': name,
        'age': int(age) if age else None,
        'certificate_file': certificate_file,
        'disability_type': None,
        'created_at': datetime.utcnow()
    }
    result = students_collection.insert_one(student)
    student['_id'] = result.inserted_id
    student['id'] = str(result.inserted_id)
    del student['_id']
    return student

def update_student(student_id, ngo_id, name, age, certificate_file=None):
    """Update student information. Returns True if successful."""
    if not ObjectId.is_valid(student_id):
        return False
    update_data = {'name': name, 'age': int(age) if age else None}
    if certificate_file:
        update_data['certificate_file'] = certificate_file
    result = students_collection.update_one(
        {'_id': ObjectId(student_id), 'ngo_id': str(ngo_id)},
        {'$set': update_data}
    )
    return result.modified_count > 0

def delete_student(student_id, ngo_id):
    """Delete a student. Returns True if deleted."""
    if not ObjectId.is_valid(student_id):
        return False
    result = students_collection.delete_one({'_id': ObjectId(student_id), 'ngo_id': str(ngo_id)})
    return result.deleted_count > 0

# Inside models/mongo_models.py
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

def update_user(user_id, full_name, email):
    # check email not used by another user
    existing = users_collection.find_one({'email': email, '_id': {'$ne': ObjectId(user_id)}})
    if existing:
        return False
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'full_name': full_name, 'email': email}}
    )
    return True

def change_user_password(user_id, current_password, new_password):
    user = find_user_by_id(user_id)
    if not user or not check_password_hash(user['password_hash'], current_password):
        return False, "Current password is incorrect"
    new_hash = generate_password_hash(new_password)
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password_hash': new_hash}}
    )
    return True, "Password changed successfully"