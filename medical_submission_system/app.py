@app.route('/student_dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        report = request.form['report']
        new_report = MedicalReport(student_id=session['user_id'], start_date=start_date, end_date=end_date, report=report)
        db.session.add(new_report)
        db.session.commit()
        flash('Medical report submitted', 'success')

    return render_template('student_dashboard.html'

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_system.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    medical_reports = db.relationship('MedicalReport', backref='student', lazy=True)

class MedicalReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    report = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']

        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email address already registered', 'error')
            else:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                new_user = User(username=username, email=email, password=hashed_password, user_type=user_type)
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful', 'success')
                return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'administration':
        return redirect(url_for('login'))

    users = User.query.filter_by(user_type='student').all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/approve_report/<int:report_id>')
def approve_report(report_id):
    if 'user_id' not in session or session['user_type'] != 'medical_officer':
        return redirect(url_for('login'))

    report = MedicalReport.query.get(report_id)
    report.status = 'Approved'
    db.session.commit()
    flash('Report approved', 'success')
    return redirect(url_for('medical_officer_dashboard'))

    @app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_type'] = user.user_type
            if user.user_type == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.user_type == 'medical_officer':
                return redirect(url_for('medical_officer_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')



