import os
import tempfile

import pytest

from berry_cam_server import create_app, Config


@pytest.fixture
def app():
    """
    A test flask app. Uses config file in this directory and temporary directory for upload.

    :return: An app instance
    :rtype: Flask
    """
    # Copy config to temporary directory, to have always a clean config even on writes (e.g. on updates of api keys)
    with tempfile.NamedTemporaryFile() as temp_config:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf.yaml')) as test_config:
            temp_config.write(test_config.read().encode('utf-8'))
            temp_config.flush()

        Config.config_file = temp_config.name

        # Use temp dir for image uploads
        with tempfile.TemporaryDirectory() as upload_dir:
            app = create_app({
                'TESTING': True,
                'SECRET_KEY': 'dev',
                'UPLOAD_DIR': upload_dir
            })
            yield app


@pytest.fixture
def client(app):
    """
    Returns a FlaskClient instance for a given app.

    :param app: The app to get the client from.
    :return: A client instance
    :rtype: FlaskClient
    """
    return app.test_client()


class AuthActions:
    """
    This class handles authentication related functionality from tester point of view.
    It provides functions to login and logout from the system.
    """

    def __init__(self, client):
        """
        Creates a new AuthActions instance.

        :param FlaskClient client: The client to use for login and logout actions.
        """
        self._client = client

    def login(self, username='test', password='test'):
        """
        Will login using given parameters. Default are valid credentials.

        :param str username: The username to use for login.
        :param str password: The password to use for login.
        """
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        """
        Log out from the system.
        """
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """
    Returns an AuthActions object to interact with authentication.

    :param FlaskClient client: The client to use for login and logout actions.
    :return: An authentication object
    :rtype: AuthActions
    """
    return AuthActions(client)
