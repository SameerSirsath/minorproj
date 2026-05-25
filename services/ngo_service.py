from models.mongo_models import get_all_students, add_student, update_student, delete_student

class NGOStudentService:
    @staticmethod
    def get_all_students(ngo_id):
        return get_all_students(ngo_id)
    
    @staticmethod
    def add_student(ngo_id, name, age, certificate_file=None):
        student = add_student(ngo_id, name, age, certificate_file)
        return student, None
    
    @staticmethod
    def update_student(student_id, ngo_id, name, age, certificate_file=None):
        success = update_student(student_id, ngo_id, name, age, certificate_file)
        if success:
            return {'id': student_id, 'name': name, 'age': age, 'certificate_file': certificate_file}, None
        return None, 'Student not found'
    
    @staticmethod
    def delete_student(student_id, ngo_id):
        success = delete_student(student_id, ngo_id)
        return success, None if success else 'Student not found'