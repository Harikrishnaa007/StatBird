import tweepy
from flask import Blueprint, render_template, session, redirect, url_for, request
from app.db import get_collection  # Import the function to get the MongoDB collection

# Define the 'unfollow' blueprint
unfollow_bp = Blueprint('unfollow', __name__)

# Function to unfollow a user using Twitter API v2 (with Tweepy v4.x.x)
def unfollow_user(user_data, target_username):
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
        # Get the user ID of the target user
        target_user = client.get_user(username=target_username)
        target_user_id = target_user.data.id

        # Unfollow the target user
        response = client.unfollow_user(target_user_id)
        print(response)  # Log the response
        return True
    except tweepy.TweepyException as e:
        # Log the error and return failure
        print(f"Error unfollowing user: {e}")
        return False

# Route to unfollow a user
@unfollow_bp.route('/unfollow', methods=['GET', 'POST'])
def unfollow():
    if 'user' not in session:
        # Redirect to login page if the user is not logged in
        return redirect(url_for('auth.login'))

    username = session['user']
    user_data = get_collection().find_one({"username": username})  # Access MongoDB collection via get_collection

    if request.method == 'POST':
        target_username = request.form['target_username']
        
        if not target_username:
            # Display an error if no target username is provided
            return render_template('unfollow.html', error="Username cannot be empty.")
        
        # Call the function to unfollow the user
        success = unfollow_user(user_data, target_username)
        
        if success:
            # Redirect to the general page after unfollowing successfully
            return redirect(url_for('general.general_page'))
        else:
            # Show error message if unfollowing failed
            return render_template('unfollow.html', error="Failed to unfollow user. Please try again.")
    
    # Render the page for GET requests (initial form)
    return render_template('unfollow.html')
