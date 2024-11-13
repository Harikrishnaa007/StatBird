import os
from flask import Flask, redirect, url_for,session
from pymongo import MongoClient
from dotenv import load_dotenv
from app.auth.auth import auth_bp  # Import auth blueprint
from app.dashboard.dashboard import dashboard_bp  # Import dashboard blueprint
from app.news.news import news_bp #Import news blueprint
from app.usearch.usearch import usearch_bp # Import the usearch blueprint
from app.post.post import post_bp # Import the post blueprint
from app.general.general import general_bp # Import the general blueprint
from app.follow.follow import follow_bp # Import the follow blueprint
from app.unfollow.unfollow import unfollow_bp # Import the unfollow blueprint
from app.retweet.retweet import retweet_bp # Import the retweet blueprint
from app.tsearch.tsearch import tsearch_bp # Import the tsearch blueprint
from app.followgp.followgp import followgp_bp # Import the followgp blueprint

# Load environment variables
load_dotenv()

# Retrieve MongoDB URI from environment variable
mongo_uri = os.getenv("MONGO_URI")

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize the MongoDB client
client = MongoClient(mongo_uri)
db = client["Statbird"]
collection = db["V1"]

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register auth blueprint with the '/auth' prefix
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')  # Register dashboard blueprint with the '/dashboard' prefix
app.register_blueprint(news_bp, url_prefix='/news')  # Register news blueprint
app.register_blueprint(usearch_bp, url_prefix='/usearch')  # Register usearch blueprint
app.register_blueprint(post_bp, url_prefix='/post')  # Register post blueprint
app.register_blueprint(general_bp, url_prefix='/general')  # Register general blueprint
app.register_blueprint(follow_bp, url_prefix='/follow')  # Register follow blueprint
app.register_blueprint(unfollow_bp, url_prefix='/unfollow') # Register unfollow blueprint
app.register_blueprint(retweet_bp, url_prefix='/retweet') # Register retweet blueprint
app.register_blueprint(tsearch_bp,url_prefix='/tsearch') # Register tsearch blueprint
app.register_blueprint(followgp_bp,url_prefix='/followgp') #Register followgp blueprint

# Define a route for the root URL '/'
@app.route('/')
def home():
    # Redirect user to the login page if not authenticated
    # Or to the dashboard if authenticated
    if 'user' in session:
        return redirect(url_for('dashboard.dashboard'))  # Redirect to dashboard if logged in
    return redirect(url_for('auth.home'))  # Redirect to login page if not logged in

if __name__ == "__main__":
    app.run(debug=True)