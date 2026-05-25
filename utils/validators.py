import re

def validate_user_input(data):
    """Validate user registration/login input"""
    
    # Required fields
    required_fields = ['fullname', 'username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field].strip():
            return f"{field.replace('_', ' ').title()} is required"
    
    # Email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return "Invalid email format"
    
    # Username validation
    if len(data['username']) < 3:
        return "Username must be at least 3 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', data['username']):
        return "Username can only contain letters, numbers, and underscores"
    
    # Password validation
    if len(data['password']) < 6:
        return "Password must be at least 6 characters"
    
    return None

def validate_student_data(data):
    """Validate student data for NGO"""
    
    if 'name' not in data or not data['name'].strip():
        return "Student name is required"
    
    if 'age' in data and data['age']:
        try:
            age = int(data['age'])
            if age < 0 or age > 120:
                return "Age must be between 0 and 120"
        except ValueError:
            return "Age must be a number"
    
    return None