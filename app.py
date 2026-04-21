import os
import base64
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nang4_studio_vscode_secure')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nang4_studio.db'
db = SQLAlchemy(app)

# 預約時段
BOOKING_TIMES = ['09:00', '10:30', '12:00', '14:00', '16:00', '18:00']

# 語系設定
LANG_DICT = {
    'zh': {
        'brand': '能樣陶室 NANG4 JOENG6 STUDIO',
        'login': '會員登入', 'register': '註冊新會員', 'email': '電子郵件 Email', 'pw': '密碼',
        'username': '稱呼', 'hrs': '剩餘時數', 'book_now': '立即預約', 'submit': '確認預約',
        'logout': '登出', 'admin_title': '會員管理與 Top-up', 'topup_btn': '確認充值',
        'no_acct': '還沒有帳戶？按此註冊', 'wheel': '陶輪', 'hand': '手捏陶土',
        'booking_date': '預約日期', 'booking_type': '課程類型', 'booking_time': '預約時段', 'booking_success': '預約成功！',
        'error_past_date': '無法預約過去的日期', 'error_insufficient_hours': '時數不足',
        'error_email_exists': '此電郵已被註冊', 'error_invalid_password': '密碼或電郵錯誤',
        'password_confirm': '確認密碼', 'error_password_mismatch': '密碼不相符'
    },
    'en': {
        'brand': 'NANG4 JOENG6 STUDIO',
        'login': 'Login', 'register': 'Register', 'email': 'Email', 'pw': 'Password',
        'username': 'Name', 'hrs': 'Hours Left', 'book_now': 'Book Now', 'submit': 'Confirm Booking',
        'logout': 'Logout', 'admin_title': 'Member & Top-up', 'topup_btn': 'Top-up',
        'no_acct': "Don't have an account? Register here", 'wheel': 'Pottery Wheel', 'hand': 'Hand Building',
        'booking_date': 'Booking Date', 'booking_type': 'Course Type', 'booking_time': 'Booking Time', 'booking_success': 'Booking Confirmed!',
        'error_past_date': 'Cannot book past dates', 'error_insufficient_hours': 'Insufficient hours',
        'error_email_exists': 'Email already registered', 'error_invalid_password': 'Invalid email or password',
        'password_confirm': 'Confirm Password', 'error_password_mismatch': 'Passwords do not match'
    }
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))
    remaining_hours = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    booking_type = db.Column(db.String(50), nullable=False)
    booking_time = db.Column(db.String(50), nullable=False, default='09:00')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))

def get_icon_base64():
    try:
        with open("logo.png", "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    except FileNotFoundError:
        return None

@app.before_request
def init():
    if 'lang' not in session:
        session['lang'] = 'zh'

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in LANG_DICT:
        session['lang'] = lang
    return redirect(request.referrer or '/')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('layout.html', page='index', t=LANG_DICT[session['lang']], user=user, icon=get_icon_base64())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash(LANG_DICT[session['lang']]['error_invalid_password'], 'error')
            return render_template('layout.html', page='login', t=LANG_DICT[session['lang']], icon=get_icon_base64())
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect(url_for('index'))
        
        flash(LANG_DICT[session['lang']]['error_invalid_password'], 'error')
    
    return render_template('layout.html', page='login', t=LANG_DICT[session['lang']], icon=get_icon_base64())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if not email or not username or not password:
            flash(LANG_DICT[session['lang']]['error_invalid_password'], 'error')
            return render_template('layout.html', page='register', t=LANG_DICT[session['lang']], icon=get_icon_base64())
        
        if password != password_confirm:
            flash(LANG_DICT[session['lang']]['error_password_mismatch'], 'error')
            return render_template('layout.html', page='register', t=LANG_DICT[session['lang']], icon=get_icon_base64())
        
        if User.query.filter_by(email=email).first():
            flash(LANG_DICT[session['lang']]['error_email_exists'], 'error')
            return render_template('layout.html', page='register', t=LANG_DICT[session['lang']], icon=get_icon_base64())
        
        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration.', 'error')
    
    return render_template('layout.html', page='register', t=LANG_DICT[session['lang']], icon=get_icon_base64())

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        booking_date_str = request.form.get('booking_date')
        booking_type = request.form.get('booking_type')
        booking_time = request.form.get('booking_time')
        
        try:
            booking_date = datetime.fromisoformat(booking_date_str)
            
            if booking_date.date() < datetime.now().date():
                flash(LANG_DICT[session['lang']]['error_past_date'], 'error')
                return redirect(url_for('index'))
            
            if user.remaining_hours < 1:
                flash(LANG_DICT[session['lang']]['error_insufficient_hours'], 'error')
                return redirect(url_for('index'))
            
            booking = Booking(
                user_id=user.id,
                booking_date=booking_date,
                booking_type=booking_type,
                booking_time=booking_time
            )
            user.remaining_hours -= 1
            
            db.session.add(booking)
            db.session.commit()
            
            flash(LANG_DICT[session['lang']]['booking_success'], 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while booking.', 'error')
    
    return render_template('layout.html', page='index', t=LANG_DICT[session['lang']], user=user, icon=get_icon_base64(), booking_times=BOOKING_TIMES)

@app.route('/nang4_topup', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))
    
    admin_user = User.query.get(session['user_id'])
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@nang4joeng6.studio').lower()
    if not admin_user or admin_user.email.lower() != admin_email:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        hrs = request.form.get('hrs', '0')
        
        try:
            hours = float(hrs)
            user = User.query.filter_by(email=email).first()
            if user:
                user.remaining_hours += hours
                db.session.commit()
                flash(f"Top-up successful! {user.username} now has {user.remaining_hours}h", 'success')
            else:
                flash('User not found', 'error')
        except ValueError:
            flash('Invalid hours value', 'error')
    
    users = User.query.all()
    return render_template('layout.html', page='admin', t=LANG_DICT[session['lang']], all_users=users, icon=get_icon_base64())

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
