from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from app.models import db, User

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(username=username, email=email)
        user.password = password  # Hashes the password
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        # Validate the user and password
        if not user or not user.check_password(password):
            return render_template('login.html', error="Invalid email or password")

        # Log the user in
        login_user(user)

        # Redirect to a user dashboard or homepage
        return redirect(url_for('auth.dashboard'))

    return render_template('login.html')


@auth_routes.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated

    return render_template('dashboard.html', user=current_user)


@auth_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
