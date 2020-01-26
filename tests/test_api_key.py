from http import HTTPStatus
from urllib.parse import urlparse

from flask import g

from berry_cam_server import Config


def test_api_key_no_login(client):
    """
    Test that redirect to login is shown if user is not logged in.

    :param FlaskClient client: The client to run the test with.
    """
    with client:
        response = client.get('/api_key/')

        # Response should be redirect to login
        assert response.status_code == HTTPStatus.FOUND
        assert urlparse(response.location).path == '/auth/login'


def test_api_key_login(client, auth):
    """
    Tests that logged in user sees a proper page if no images are available.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        response = client.get('/api_key/')

        # Now we should see the api key and a regeneration information
        api_key = Config.get_user_config('test')["api_key"]

        assert api_key.encode('utf-8') in response.data
        assert b'regenerate' in response.data.lower()


def test_api_key_regeneration(client, auth):
    """
    Tests that logged in user sees a proper page if no images are available.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        # Get the api key before update
        old_api_key = Config.get_user_config('test')['api_key']

        response = client.get('/api_key/regenerate_key')

        assert response.status_code == HTTPStatus.FOUND
        assert urlparse(response.location).path == '/api_key/'

        # Check update of configuration
        new_api_key = Config.get_user_config('test')['api_key']
        assert new_api_key != old_api_key
        assert g.user['api_key'] == new_api_key

        # Check that new api key is also shown on redirected page
        response = client.get(response.location)
        assert new_api_key.encode('utf-8') in response.data
