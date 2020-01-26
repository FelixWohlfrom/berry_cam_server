from flask import Blueprint, render_template, url_for, redirect, g

from .common.conf import Config
from .auth import login_required

bp = Blueprint('api_key', __name__, url_prefix='/api_key')


@bp.route('/')
@login_required
def index():
    """
    Displays the api key information.

    :return: The html
    :rtype: str
    """
    return render_template('api_key.html')


@bp.route('/regenerate_key')
@login_required
def regenerate_key():
    """
    Will create a new api key, thus revoking the old one, and refresh the page.

    :return: A redirect to the api key index page
    :rtype: Redirect
    """

    g.user["api_key"] = Config.update_api_key(g.user["username"])
    return redirect(url_for('api_key.index'))
