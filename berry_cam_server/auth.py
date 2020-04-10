
import functools
import hashlib
from http import HTTPStatus

from flask import Blueprint, flash, redirect, url_for, render_template, request, session, g
from flask_restx import abort, reqparse

from .common.conf import Config

bp = Blueprint('auth', __name__, url_prefix='/auth')

api_key_parser = reqparse.RequestParser()
api_key_parser.add_argument('api_key', type=str, help='The api key to authenticate against the system.', required=True)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Will handle the login to the system.

    :return: On successful login, redirect to index page, otherwise template for login.
    :rtype: Redirect or str
    """

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_config = Config.get_user_config(username)
        if not user_config or \
                hashlib.sha512(password.encode('utf-8')).hexdigest() != user_config["password"]:
            flash("Invalid credentials")

        else:
            session.clear()
            session['username'] = username
            return redirect(url_for('index'))

    return render_template('login.html')


@bp.route('/logout')
def logout():
    """
    Handler for logout actions.
    :return: Redirect to index page
    :rtype: Redirect
    """
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    """
    Initialisation of user info session.
    Called for each request and initializing global information for current user.
    """
    username = session.get('username')

    if not username:
        g.user = None
    else:
        g.user = Config.get_user_config(username)
        g.user["username"] = username


def login_required(view):
    """
    Decorator to check if the user is currently logged in.
    Can be used for each function that requires logged in user.

    :param function view: The view to check.
    :return: Either the result of called view or redirect to login.
    :rtype: Any or Redirect
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def api_key_required(func):
    """
    Will check for api_key entry in REST api. If api key is missing, it will abort the call and display
    a proper message. Same also if the api key is invalid.

    :param function func: The REST function to check
    :return: Either an http response containing information that the api key is missing or the function result.
    :rtype: Response or Any
    """
    @functools.wraps(func)
    def wrapped_command(*args, **kwargs):
        # This will also check that mandatory api key is available in arguments and stop execution if not.
        custom_args = api_key_parser.parse_args()

        if custom_args.api_key not in Config.get_api_keys():
            abort(HTTPStatus.FORBIDDEN, "Invalid api_key given")

        return func(*args, **kwargs)

    return wrapped_command
