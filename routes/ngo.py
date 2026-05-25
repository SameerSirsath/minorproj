from flask import Blueprint, render_template, session, request, jsonify
from utils.helpers import login_required, ngo_required
from services.ngo_service import NGOStudentService

ngo_bp = Blueprint('ngo', __name__)

@ngo_bp.route('/ngo/dashboard')
@login_required
@ngo_required
def dashboard():
    return render_template('sample.html', user=session)

@ngo_bp.route('/ngo/analyze')
@login_required
@ngo_required
def analyze():
    return render_template('login_ngo.html', user=session)

@ngo_bp.route('/api/students', methods=['GET'])
@login_required
@ngo_required
def get_students():
    students = NGOStudentService.get_all_students(session['user_id'])
    return jsonify(students)

@ngo_bp.route('/api/students', methods=['POST'])
@login_required
@ngo_required
def add_student():
    name = request.form.get('name')
    age = request.form.get('age')
    certificate_file = request.files.get('certificate')
    
    certificate_filename = NGOStudentService.save_certificate(certificate_file)
    
    student, error = NGOStudentService.add_student(
        session['user_id'], name, age, certificate_filename
    )
    
    if error:
        return jsonify({'success': False, 'error': error})
    
    return jsonify({'success': True, 'student': student.to_dict()})

@ngo_bp.route('/api/students/<int:student_id>', methods=['PUT'])
@login_required
@ngo_required
def update_student(student_id):
    name = request.form.get('name')
    age = request.form.get('age')
    certificate_file = request.files.get('certificate')
    
    certificate_filename = None
    if certificate_file:
        certificate_filename = NGOStudentService.save_certificate(certificate_file)
    
    student, error = NGOStudentService.update_student(
        student_id, session['user_id'], name, age, certificate_filename
    )
    
    if error:
        return jsonify({'success': False, 'error': error})
    
    return jsonify({'success': True, 'student': student.to_dict()})

@ngo_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@login_required
@ngo_required
def delete_student(student_id):
    success, error = NGOStudentService.delete_student(student_id, session['user_id'])
    
    if error:
        return jsonify({'success': False, 'error': error})
    
    return jsonify({'success': True})