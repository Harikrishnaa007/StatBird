import tweepy
from flask import Blueprint, render_template, session, redirect, url_for, request
from app.db import get_collection  # Import the MongoDB collection

# Define the 'follow' blueprint
follow_bp = Blueprint('follow', __name__)

# Function to follow a user using Twitter API v2 (with Tweepy v4.x.x)
def follow_user(user_data, target_username):
    # Extract the access tokens from the user's data
    access_token = user_data['access_t']
    access_token_secret = user_data['access_tsec']
    
    if not access_token or not access_token_secret:
        print("Access token or secret is missing or invalid.")
        return False
    
    # OAuth 1.0a credentials for Twitter API
    consumer_key = user_data['api_key']
    consumer_secret = user_data['api_keysec']
    
    # Initialize Tweepy with OAuth 1.0a for API v2
    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
    client = tweepy.Client(bearer_token=user_data['bearer_token'], 
                           consumer_key=consumer_key, 
                           consumer_secret=consumer_secret, 
                           access_token=access_token, 
                           access_token_secret=access_token_secret)

    try:
        # Use Twitter API v2 to follow a user by their username
        # You need to fetch the user ID first based on the username
        user_info = client.get_user(username=target_username)
        
        # Now use the user ID to follow the user
        response = client.follow_user(user_info.data.id)
        print(response)  # Log the response for debugging
        
        if response.data:
            return True
        else:
            return False
    except tweepy.TweepyException as e:
        # Log the error and return failure
        print(f"Error following user: {e}")
        return False

# Route to follow a user
@follow_bp.route('/follow', methods=['GET', 'POST'])
def follow():
    if 'user' not in session:
        # Redirect to login page if the user is not logged in
        return redirect(url_for('auth.login'))

    username = session['user']
    user_data = get_collection().find_one({"username": username})

    if request.method == 'POST':
        target_username = request.form['target_username']
        
        if not target_username:
            # Display an error if no target username is provided
            return render_template('follow.html', error="Target username cannot be empty.")
        
        # Call the function to follow the user
        success = follow_user(user_data, target_username)
        
        if success:
            # Redirect to the general page after successfully following the user
            return redirect(url_for('general.general_page'))
        else:
            # Show error message if following the user failed
            return render_template('follow.html', error="Failed to follow user. Please try again.")
    
    # Render the page for GET requests (initial form)
    return render_template('follow.html')
