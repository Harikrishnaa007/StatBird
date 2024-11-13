from flask import Blueprint, render_template, redirect, url_for

# Create a new Blueprint for general actions
general_bp = Blueprint('general', __name__)

# Route for the general page
@general_bp.route('/general')
def general_page():
    return render_template('general.html')  # Render the general page (not redirect)

# Route for redirecting to Post action
@general_bp.route('/post')
def redirect_to_post():
    return redirect(url_for('post.post'))  # Redirect to post.py route

# Route for redirecting to Retweet action
@general_bp.route('/retweet')
def redirect_to_retweet():
    return redirect(url_for('retweet.retweet_view'))  # Redirect to retweet.py route

# Route for redirecting to Follow action
@general_bp.route('/follow')
def redirect_to_follow():
    return redirect(url_for('follow.follow'))  # Redirect to follow.py route

# Route for redirecting to Unfollow action
@general_bp.route('/unfollow')
def redirect_to_unfollow():
    return redirect(url_for('unfollow.unfollow'))  # Redirect to unfollow.py route
