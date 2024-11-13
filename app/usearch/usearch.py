import tweepy
from flask import Blueprint, render_template, session, redirect, url_for, request
from app import collection  # Import the MongoDB collection

# Define the 'usearch' blueprint
usearch_bp = Blueprint('usearch', __name__)

# Function to get Twitter user info (including public metrics and verification status)
def get_twitter_user_info(username, bearer_token):
    client = tweepy.Client(bearer_token=bearer_token)  # Use tweepy.Client for API v2
    
    try:
        # Fetch user information for the specified username
        user = client.get_user(username=username, user_fields=["public_metrics", "verified", "username", "profile_image_url"])
        
        if user and user.data:
            return user.data  # Return the 'data' attribute which contains the actual user data
        else:
            print("Error: No user data found.")
            return None
    except tweepy.TweepyException as e:
        print(f"Error fetching user data from Twitter: {e}")
        return None

@usearch_bp.route('/', methods=['GET', 'POST'])
def usearch():
    if 'user' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    username = session['user']
    user_data = collection.find_one({"username": username})

    # Extract user information from MongoDB
    user_info = {
        'username': user_data.get('username'),
        'email': user_data.get('email'),
    }

    twitter_info = None

    if request.method == 'POST':
        # Get the Twitter username from the form
        search_username = request.form.get('twitter_username')

        if search_username:
            # Fetch the Bearer Token from the MongoDB user data to authenticate with Twitter API
            bearer_token = user_data.get('bearer_token')

            if bearer_token:
                twitter_info = get_twitter_user_info(search_username, bearer_token)

    return render_template('usearch.html', user_info=user_info, twitter_info=twitter_info)
