import tweepy
import requests  # To handle URL expansion
from flask import Blueprint, render_template, session, redirect, url_for
from app.db import get_collection  # Import the function to get the MongoDB collection

# Define the 'news' blueprint
news_bp = Blueprint('news', __name__)

# Function to expand shortened URLs
def expand_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except requests.RequestException:
        return url  # Return the original shortened URL if there's an issue

# Function to authenticate with Twitter API v2 and fetch recent news-related tweets
def get_trending_news_tweets(user_data):
    # Extract Bearer Token from the MongoDB user data
    bearer_token = user_data['bearer_token']

    # Authenticate with Twitter API v2 using Bearer Token
    client = tweepy.Client(bearer_token=bearer_token)

    query = "#news OR #BreakingNews OR #WorldNews OR #Headlines"  # News-related hashtags and topics
    try:
        # Fetch recent tweets with text, user, and referenced tweet expansions
        tweets = client.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=["text"],
            expansions=["referenced_tweets.id", "author_id"],
            user_fields=["username"]
        )

        # Prepare a dictionary to map author_id to username
        user_dict = {user.id: user.username for user in tweets.includes["users"]}

        # Prepare a list to store full tweet data
        tweet_data = []

        if tweets.data:
            for tweet in tweets.data:
                # Determine if it's a retweet
                is_retweet = False
                full_text = tweet.text
                if tweet.referenced_tweets:
                    is_retweet = True
                    referenced_id = tweet.referenced_tweets[0].id
                    original_tweet = next((ref for ref in tweets.includes["tweets"] if ref.id == referenced_id), None)
                    if original_tweet:
                        full_text = original_tweet.text

                # Replace shortened URLs in the tweet text
                words = full_text.split()
                for i, word in enumerate(words):
                    if word.startswith("https://t.co/"):
                        words[i] = expand_url(word)  # Replace shortened URL with expanded one
                full_text = " ".join(words)

                # Append the full tweet data with expanded text and the author's username
                tweet_data.append({
                    'text': full_text,
                    'author_username': user_dict.get(tweet.author_id, "Unknown"),  # Get the username from the user dictionary
                    'is_retweet': is_retweet  # Add retweet flag
                })

        return tweet_data  # Return the tweet data with full text

    except tweepy.TweepyException as e:
        print(f"Error fetching tweets: {e}")
        return None

# Route for the news dashboard
@news_bp.route('/news')
def news_dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    username = session['user']
    user_data = get_collection().find_one({"username": username})  # Use get_collection() for MongoDB query

    # Fetch news-related tweets using the user's Bearer Token
    tweets = get_trending_news_tweets(user_data)

    return render_template('news_dashboard.html', user_data=user_data, tweets=tweets)
