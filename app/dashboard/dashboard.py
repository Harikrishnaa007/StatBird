import tweepy
from flask import Blueprint, render_template, session, redirect, url_for
from app.db import get_collection  # Import the function to get the MongoDB collection

# Define the 'dashboard' blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Function to get Twitter user info (including follower count and profile image)
def get_twitter_user_info(user_data):
    bearer_token = user_data['bearer_token']  # Bearer token from MongoDB
    client = tweepy.Client(bearer_token=bearer_token)  # Use tweepy.Client for API v2
    m = user_data['tuser']  # Get username from MongoDB

    try:
        # Fetch user information for the authenticated user with 'public_metrics', 'verified', 'username', and 'profile_image_url'
        user = client.get_user(username=m, user_fields=["public_metrics", "verified", "username", "profile_image_url"])

        if user and user.data:
            # Print the entire user data to check for missing fields
            print("User Data:", user.data)
            return user.data  # Return the 'data' attribute which contains the actual user data
        else:
            print("Error: No user data found.")
            return None
    except tweepy.TweepyException as e:
        print(f"Error fetching user data from Twitter: {e}")
        return None

@dashboard_bp.route('/')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    username = session['user']
    user_data = get_collection().find_one({"username": username})  # Use get_collection to get MongoDB collection

    # Extract user information from MongoDB
    user_info = {
        'username': user_data.get('username'),
        'email': user_data.get('email'),
    }

    # Fetch the Bearer Token from the MongoDB user data to authenticate with Twitter API
    bearer_token = user_data.get('bearer_token')

    if bearer_token:
        twitter_info = get_twitter_user_info(user_data)

        if twitter_info:
            # Access public_metrics to get followers and following count
            user_info['followers_count'] = twitter_info.get('public_metrics', {}).get('followers_count', 0)
            user_info['following_count'] = twitter_info.get('public_metrics', {}).get('following_count', 0)
            user_info['verified'] = twitter_info.get('verified', False)  # Check if verified

            # Add the profile image URL to user_info
            user_info['profile_image_url'] = twitter_info.get('profile_image_url', None)
        else:
            user_info['followers_count'] = 0
            user_info['following_count'] = 0
            user_info['verified'] = False
            user_info['profile_image_url'] = None
    else:
        user_info['followers_count'] = 0
        user_info['following_count'] = 0
        user_info['verified'] = False
        user_info['profile_image_url'] = None

    return render_template('dashboard.html', user_info=user_info)
