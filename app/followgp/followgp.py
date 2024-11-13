import tweepy
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import collection  # Import the MongoDB collection

# Define the 'followgp' blueprint
followgp_bp = Blueprint('followgp', __name__)

# Function to get the follower and following count
def get_follow_counts(username, bearer_token):
    client = tweepy.Client(bearer_token=bearer_token)
    
    try:
        # Fetch user information for the specified username including public metrics
        user = client.get_user(username=username, user_fields=["public_metrics"])
        
        if user and user.data:
            # Extract followers and following counts from public metrics
            followers_count = user.data.public_metrics["followers_count"]
            following_count = user.data.public_metrics["following_count"]
            return followers_count, following_count
        else:
            print("Error: No user data found.")
            return None, None
    except tweepy.TweepyException as e:
        print(f"Error fetching user data from Twitter: {e}")
        return None, None

# Define the route for the Follow Distribution page
@followgp_bp.route('/', methods=['GET', 'POST'])
def followgp():
    # Check if the user is logged in by checking session
    if 'user' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    # Get the current logged-in user's username from session
    username = session['user']
    user_data = collection.find_one({"username": username})

    # Extract user information from MongoDB
    user_info = {
        'username': user_data.get('username'),
        'email': user_data.get('email'),
        'profile_image_url': user_data.get('profile_image_url', 'https://via.placeholder.com/100'),  # Default image if none
    }

    # Initialize default follower and following counts to None
    followers_count = None
    following_count = None

    # Handle the POST request when the user submits the Twitter username form
    if request.method == 'POST':
        search_username = request.form.get('twitter_username')

        if search_username:
            # Fetch the Bearer Token from MongoDB user data to authenticate with Twitter API
            bearer_token = user_data.get('bearer_token')

            if bearer_token:
                # Get the follower and following counts from Twitter API
                followers_count, following_count = get_follow_counts(search_username, bearer_token)

                # If no data found, flash a message (optional, for better UX)
                if followers_count is None or following_count is None:
                    flash('Could not fetch data for the specified Twitter username. Please try again.', 'danger')
    print(followers_count,following_count)
    # Pass the data to the template for rendering
    return render_template(
        'followgp.html',
        user_info=user_info,
        followers_count=followers_count,
        following_count=following_count
    )
