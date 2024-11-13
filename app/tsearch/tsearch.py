import tweepy
import requests  # To handle URL expansion
from flask import Blueprint, render_template, session, redirect, url_for, request
from app.db import get_collection  # Import the function to get the MongoDB collection

# Define the 'tsearch' blueprint
tsearch_bp = Blueprint('tsearch', __name__)

# Function to expand shortened URLs
def expand_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except requests.RequestException:
        return url  # Return the original shortened URL if there's an issue

# Function to search tweets using Twitter API v2 and expand URLs
def tsearch_tweets(user_data, query, max_results=10):
    bearer_token = user_data.get('bearer_token')
    
    if not bearer_token:
        print("Bearer token is missing or invalid.")
        return []

    client = tweepy.Client(bearer_token=bearer_token)

    try:
        # Use Twitter API v2 to search recent tweets with the query
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["text"],
            expansions=["author_id"],
            user_fields=["username"]
        )

        user_dict = {user.id: user.username for user in tweets.includes["users"]}

        tweet_data = []
        if tweets.data:
            for tweet in tweets.data:
                full_text = tweet.text
                
                # Replace shortened URLs in the tweet text
                words = full_text.split()
                for i, word in enumerate(words):
                    if word.startswith("https://t.co/"):
                        words[i] = expand_url(word)
                full_text = " ".join(words)

                # Append the tweet data with expanded text and the author's username
                tweet_data.append({
                    'text': full_text,
                    'author_username': user_dict.get(tweet.author_id, "Unknown")
                })

        return tweet_data

    except tweepy.TweepyException as e:
        print(f"Error searching tweets: {e}")
        return []

# Route to search tweets
@tsearch_bp.route('/tsearch', methods=['GET', 'POST'])
def tsearch_view():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    username = session['user']
    user_data = get_collection().find_one({"username": username})  # Access MongoDB collection via get_collection

    tweets = []
    if request.method == 'POST':
        query = request.form.get('query')
        
        if not query:
            return render_template('tsearch.html', error="Search query cannot be empty.")
        
        tweets = tsearch_tweets(user_data, query)
        
        if not tweets:
            return render_template('tsearch.html', error="No tweets found or search failed.")
    
    return render_template('tsearch.html', tweets=tweets)
