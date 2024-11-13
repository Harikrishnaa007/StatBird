import tweepy
from flask import Blueprint, render_template, session, redirect, url_for, request
from app import collection  # Import the MongoDB collection

# Define the 'retweet' blueprint
retweet_bp = Blueprint('retweet', __name__)

# Function to retweet a tweet using Twitter API v2 (with Tweepy v4.x.x)
def retweet(user_data, tweet_id):
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
    client = tweepy.Client(
        bearer_token=user_data['bearer_token'],
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    try:
        # Use Twitter API v2 to retweet the tweet (create_retweet method)
        response = client.retweet(tweet_id=tweet_id)
        print(response)  # Log the retweet response
        return True
    except tweepy.TweepyException as e:
        # Log the error and return failure
        print(f"Error retweeting: {e}")
        return False

# Route to retweet a tweet
@retweet_bp.route('/retweet', methods=['GET', 'POST'])
def retweet_view():
    if 'user' not in session:
        # Redirect to login page if the user is not logged in
        return redirect(url_for('auth.login'))

    username = session['user']
    user_data = collection.find_one({"username": username})

    if not user_data:
        return redirect(url_for('auth.login'))  # Ensure user data is valid

    if request.method == 'POST':
        tweet_id = request.form.get('tweet_id')
        
        if not tweet_id:
            # Display an error if no tweet ID is provided
            return render_template('retweet.html', error="Tweet ID cannot be empty.")
        
        # Call the function to retweet
        success = retweet(user_data, tweet_id)
        
        if success:
            # Redirect to the general page after successful retweet
            return redirect(url_for('general.general_page'))
        else:
            # Show error message if retweeting failed
            return render_template('retweet.html', error="Failed to retweet. Please try again.")
    
    # Render the page for GET requests (initial form)
    return render_template('retweet.html')
