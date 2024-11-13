import tweepy
from flask import Blueprint, render_template, session, redirect, url_for, request
from app import collection  # Import the MongoDB collection

# Define the 'post' blueprint
post_bp = Blueprint('post', __name__)

# Function to post a tweet using Twitter API v2 (with Tweepy v4.x.x)
def post_tweet(user_data, tweet_text):
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
        # Use Twitter API v2 to post a tweet (create_tweet method)
        response = client.create_tweet(text=tweet_text)
        print(response)  # Log the tweet response
        return True
    except tweepy.TweepyException as e:
        # Log the error and return failure
        print(f"Error posting tweet: {e}")
        return False

# Route to post a tweet
@post_bp.route('/post', methods=['GET', 'POST'])
def post():
    if 'user' not in session:
        # Redirect to login page if the user is not logged in
        return redirect(url_for('auth.login'))

    username = session['user']
    user_data = collection.find_one({"username": username})

    if request.method == 'POST':
        tweet_text = request.form['tweet_text']
        
        if not tweet_text:
            # Display an error if no tweet text is provided
            return render_template('post.html', error="Tweet text cannot be empty.")
        
        # Call the function to post the tweet
        success = post_tweet(user_data, tweet_text)
        
        if success:
            # Redirect to the general page after tweet was posted successfully
            return redirect(url_for('general.general_page'))
        else:
            # Show error message if posting failed
            return render_template('post.html', error="Failed to post tweet. Please try again.")
    
    # Render the page for GET requests (initial form)
    return render_template('post.html')
