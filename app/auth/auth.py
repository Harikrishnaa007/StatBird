from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import collection  # Import the MongoDB collection from app.py
from dotenv import load_dotenv
import tweepy
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing

# Load environment variables (if needed for other purposes)
load_dotenv()

# Define the 'auth' blueprint
auth_bp = Blueprint('auth', __name__)

# Route to home
@auth_bp.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard.dashboard'))  # Redirect to dashboard if logged in
    return redirect(url_for('auth.login'))  # Redirect to login page if not logged in

# Route to register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        bearer_token = request.form['bearer_token']  # Only if Bearer Token is needed
        tuser = request.form['tuser']
        access_t = request.form['access_t']
        access_tsec = request.form['access_tsec']
        api_key = request.form['api_key']
        api_keysec = request.form['api_keysec']

        try:
            # Check if the username already exists
            existing_user = collection.find_one({"username": username})
            if existing_user:
                flash("Username already exists! Please choose a different one.", 'error')
                return redirect(url_for('auth.register'))

            # Insert user data including API keys and access tokens
            data = {
                "username": username,
                "password": password,  # Store hashed password
                "email": email,
                "bearer_token": bearer_token,  # Optional
                "tuser": tuser,
                "access_t": access_t,
                "access_tsec": access_tsec,
                "api_key": api_key,
                "api_keysec": api_keysec,
            }
            collection.insert_one(data)
            flash("Registration successful! Please log in.", 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

# Route to login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and the password matches
        user = collection.find_one({"username": username})
        if user and user['password'] == password:
            session['user'] = user['username']
            flash("Login successful!", 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid username or password. Please try again.", 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# Route to logout
@auth_bp.route('/logout')
def logout():
    session.pop('user', None)  # Clear session data
    flash("You have been logged out.", 'info')
    return redirect(url_for('auth.login'))  # Redirect to login page after logout

# Function to get authenticated Tweepy API client using stored credentials
def get_twitter_api():
    user = collection.find_one({"username": session.get('user')})
    if user:
        auth = tweepy.OAuth1UserHandler(
            user['api_key'], 
            user['api_keysec'],
            user['access_t'],
            user['access_tsec']
        )
        return tweepy.API(auth)
    else:
        flash("Error retrieving Twitter API client.", 'error')
        return None

# Example route to use Twitter API (optional)
@auth_bp.route('/twitter_example')
def twitter_example():
    api = get_twitter_api()
    if api:
        try:
            twitter_user = api.verify_credentials()
            flash(f"Logged in as {twitter_user.screen_name}", 'success')
            return redirect(url_for('dashboard.dashboard'))
        except tweepy.TweepyException as e:
            flash(f"Twitter API error: {e}", 'error')
    else:
        flash("Twitter API client could not be created.", 'error')
    
    return redirect(url_for('auth.login'))
