import os
import datetime
from datetime import timezone
from http import HTTPStatus
from urllib.parse import urlparse

from flask import g, session

from .utils.image_generator import generate_test_images


def test_viewer_no_login(client):
    """
    Test that redirect to login is shown if user is not logged in.

    :param FlaskClient client: The client to run the test with.
    """
    with client:
        response = client.get('/')

        # Response should be redirect to login
        assert response.status_code == HTTPStatus.FOUND
        assert urlparse(response.location).path == '/auth/login'

        assert 'username' not in session
        assert not g.user


def test_viewer_login_empty(client, auth):
    """
    Tests that logged in user sees a proper page if no images are available.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        response = client.get('/')

        # Now we should see the default view with no older pictures or recent pictures
        assert response.status_code == HTTPStatus.OK
        assert b'No recent pictures.' in response.data
        assert b'No older pictures.' in response.data


def test_viewer_only_recent(app, client, auth):
    """
    Tests that logged in user sees proper information if only recent images are available.

    :param Flask app: The flask application to test.
    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    generate_test_images(app.config.get('UPLOAD_DIR'),
                         5,
                         datetime.datetime(year=2020, month=1, day=10, hour=8, minute=10, second=5))

    auth.login()

    with client:
        response = client.get('/')

        assert response.status_code == HTTPStatus.OK
        assert b'No recent pictures.' not in response.data
        assert b'No older pictures.' in response.data


def test_viewer_also_older(app, client, auth):
    """
    Tests that logged in user sees proper information if recent images and older images are available.

    :param Flask app: The flask application to test.
    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    generate_test_images(app.config.get('UPLOAD_DIR'),
                         10,
                         datetime.datetime(year=2020, month=1, day=10, hour=8, minute=10, second=5))

    auth.login()

    with client:
        response = client.get('/')

        assert response.status_code == HTTPStatus.OK
        assert b'No recent pictures.' not in response.data
        assert b'No older pictures.' not in response.data


def test_authentication_access_no_login(app, client):
    """
    Verifies that image access is prohibited if the user is not logged in.

    :param Flask app: The flask application to test.
    :param FlaskClient client: The client to run the test with.
    """
    generate_test_images(app.config.get('UPLOAD_DIR'),
                         1,
                         datetime.datetime(year=2020, month=1, day=10, hour=8, minute=10, second=5))

    with client:
        # Check for preview
        response = client.get('/previews/1578640205.jpg')
        assert response.status_code == HTTPStatus.FOUND
        assert urlparse(response.location).path == '/auth/login'

        # Check for raw image
        response = client.get('/large/1578640205.png')
        assert response.status_code == HTTPStatus.FOUND
        assert urlparse(response.location).path == '/auth/login'


def test_authentication_access_login(app, client, auth):
    """
    Verifies that image access is allowed if the user is logged in.

    :param Flask app: The flask application to test.
    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    generate_test_images(app.config.get('UPLOAD_DIR'),
                         1,
                         # We need to define utc timezone info here since we need a predictable generated name
                         datetime.datetime(year=2020, month=1, day=10, hour=8, minute=10, second=5,
                                           tzinfo=timezone.utc))
    auth.login()

    with client:
        # Check for preview
        response = client.get('/previews/1578643805.jpg')
        assert response.status_code == HTTPStatus.OK

        # Check for raw image
        response = client.get('/large/1578643805.png')
        assert response.status_code == HTTPStatus.OK


def test_cleanup_images(app, client, auth):
    """
    Tests that cleanup of images works fine and remvoes all images.

    :param Flask app: The flask application to test.
    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    generate_test_images(app.config.get('UPLOAD_DIR'),
                         10,
                         datetime.datetime(year=2020, month=1, day=10, hour=8, minute=10, second=5))

    auth.login()

    with client:
        assert os.listdir(os.path.join(app.config.get('UPLOAD_DIR'), 'raw'))
        assert os.listdir(os.path.join(app.config.get('UPLOAD_DIR'), 'previews'))

        response = client.get('/?cleanup=true', follow_redirects=True)

        assert response.status_code == HTTPStatus.OK
        assert urlparse(response.location).path == b''
        assert b'No recent pictures.' in response.data
        assert b'No older pictures.' in response.data
        assert not os.listdir(os.path.join(app.config.get('UPLOAD_DIR'), 'raw'))
        assert not os.listdir(os.path.join(app.config.get('UPLOAD_DIR'), 'previews'))