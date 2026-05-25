from flask import Blueprint, render_template, session
from utils.helpers import login_required, individual_required

individual_bp = Blueprint('individual', __name__)

@individual_bp.route('/home')
@login_required
@individual_required
def home():
    return render_template('index.html', user=session)

@individual_bp.route('/services')
@login_required
@individual_required
def services():
    return render_template('planner.html', user=session)

@individual_bp.route('/resources')
@login_required
@individual_required
def resources():
    return render_template('guide.html', user=session)

@individual_bp.route('/community')
@login_required
@individual_required
def community():
    return render_template('community.html', user=session)

@individual_bp.route('/about')
@login_required
@individual_required
def about():
    return render_template('about.html', user=session)