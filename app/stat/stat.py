from flask import Blueprint, render_template, redirect, url_for

# Create a new Blueprint for general actions
stat_bp = Blueprint('stat', __name__)

# Route for the stat page
@stat_bp.route('/stat')
def general_page():
    return render_template('stat.html')  # Render the stat page (not redirect)

# Route for redirecting to followgp action
@stat_bp.route('/followgp')
def redirect_to_post():
    return redirect(url_for('followgp.followgp'))  # Redirect to followgp.py route



