# app/__init__.py

import os
from flask import Flask, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    # Initialize the Flask app
    app = Flask(__name__)
    app.secret_key = os.urandom(24)  # For session management

    # Initialize MongoDB client
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["Statbird"]
    app.config["db"] = db  # Store the database in the app config for use in other blueprints

    # Register Blueprints
    from app.auth.auth import auth_bp
    from app.dashboard.dashboard import dashboard_bp
    from app.news.news import news_bp
    from app.usearch.usearch import usearch_bp
    from app.post.post import post_bp
    from app.general.general import general_bp
    from app.follow.follow import follow_bp
    from app.unfollow.unfollow import unfollow_bp
    from app.retweet.retweet import retweet_bp
    from app.tsearch.tsearch import tsearch_bp
    from app.followgp.followgp import followgp_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(news_bp, url_prefix='/news')
    app.register_blueprint(usearch_bp, url_prefix='/usearch')
    app.register_blueprint(post_bp, url_prefix='/post')
    app.register_blueprint(general_bp, url_prefix='/general')
    app.register_blueprint(follow_bp, url_prefix='/follow')
    app.register_blueprint(unfollow_bp, url_prefix='/unfollow')
    app.register_blueprint(retweet_bp, url_prefix='/retweet')
    app.register_blueprint(tsearch_bp, url_prefix='/tsearch')
    app.register_blueprint(followgp_bp, url_prefix='/followgp')

    # Define a route for the root URL '/'
    @app.route('/')
    def home():
        # Redirect user to the login page if not authenticated
        # Or to the dashboard if authenticated
        if 'user' in session:
            return redirect(url_for('dashboard.dashboard'))  # Redirect to dashboard if logged in
        return redirect(url_for('auth.home'))  # Redirect to login page if not logged in

    # Empty favicon route to prevent 404 errors
    @app.route('/favicon.ico')
    def favicon():
        return "", 204  # Return an empty response with a 204 No Content status

    return app

