from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('v2/dashboard.html')

@home_bp.route('/login')
def login():
    return render_template('v2/login.html')
