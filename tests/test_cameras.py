from http import HTTPStatus
from urllib.parse import urlparse
from datetime import datetime, timezone

import yaml

from berry_cam_server import Config

CAMERA_NAME = 'Test-Camera'

def update_camera_timestamp(date):
    """
    Updates the timestamp for the camera to be the given timestamp.

    :param Date date: The date to store for the camera
    """
    with open(Config.config_file, 'r') as config_file:
        config = yaml.safe_load(config_file)

    with open(Config.config_file, 'w') as config_file:
        config["cameras"][CAMERA_NAME]["last_connection"] = int(date.timestamp())
        yaml.safe_dump(config, config_file)

def test_cameras_no_login(client):
    """
    Test that redirect to login is shown if user is not logged in.

    :param FlaskClient client: The client to run the test with.
    """
    with client:
        response = client.get('/cameras/')

        # Response should be redirect to login
        assert response.status_code == HTTPStatus.FOUND
        assert urlparse(response.location).path == '/auth/login'


def test_cameras_login(client, auth):
    """
    Tests that logged in user sees a proper page if no cameras are available.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        response = client.get('/cameras/')

        assert b'no cameras' in response.data.lower()


def test_camera_available_disabled_connection_pending(client, auth):
    """
    Verifies that if a camera is disabled and there was no connection for
    quite a long time, it is displayed properly.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, False)
        test_timestamp = datetime(2020, 2, 1, 10, 15, 0, tzinfo=timezone.utc)
        update_camera_timestamp(test_timestamp)

        response = client.get('/cameras/')

        assert CAMERA_NAME.encode() in response.data
        assert test_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC').encode() in response.data
        assert b'disabled' in response.data.lower()
        assert b'connection_pending' in response.data.lower()


def test_camera_available_enabled_connection_pending(client, auth):
    """
    Verifies that if a camera is enabled and there was no connection for
    quite a long time, it is displayed properly.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, True)
        test_timestamp = datetime(2020, 2, 1, 10, 15, 0, tzinfo=timezone.utc)
        update_camera_timestamp(test_timestamp)

        response = client.get('/cameras/')

        assert CAMERA_NAME.encode() in response.data
        assert test_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC').encode() in response.data
        assert b'enabled' in response.data.lower()
        assert b'connection_pending' in response.data.lower()


def test_camera_available_disabled_connection_up_to_date(client, auth):
    """
    Verifies that if a camera is disabled and there was a recent connection,
    it is displayed properly.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, False)
        test_timestamp = datetime.now(tz=timezone.utc)
        update_camera_timestamp(test_timestamp)

        response = client.get('/cameras/')

        assert CAMERA_NAME.encode() in response.data
        assert test_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC').encode() in response.data
        assert b'disabled' in response.data.lower()
        assert b'connection_pending' not in response.data.lower()


def test_camera_available_enabled_connection_up_to_date(client, auth):
    """
    Verifies that if a camera is enabled and there was a recent connection,
    it is displayed properly.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, True)
        test_timestamp = datetime.now(tz=timezone.utc)
        update_camera_timestamp(test_timestamp)

        response = client.get('/cameras/')

        assert CAMERA_NAME.encode() in response.data
        assert test_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC').encode() in response.data
        assert b'enabled' in response.data.lower()
        assert b'connection_pending' not in response.data.lower()


def test_enable_camera(client, auth):
    """
    Verifies that enabling a camera sets the correct settings.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, False)

        response = client.get('/cameras/?name=' + CAMERA_NAME + '&enable=true',
                              follow_redirects=True)

        assert response.status_code == HTTPStatus.OK
        assert CAMERA_NAME.encode() in response.data
        assert b'disabled' in response.data.lower()

        assert Config.get_connected_cameras()[CAMERA_NAME]['enabled'] == True


def test_disable_camera(client, auth):
    """
    Verifies that disabling a camera sets the correct settings.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, True)

        response = client.get('/cameras/?name=' + CAMERA_NAME + '&enable=false',
                              follow_redirects=True)

        assert response.status_code == HTTPStatus.OK
        assert CAMERA_NAME.encode() in response.data
        assert b'enabled' in response.data.lower()

        assert Config.get_connected_cameras()[CAMERA_NAME]['enabled'] == False


def test_delete_camera(client, auth):
    """
    Verifies that deletion of a camera removes the camera.

    :param FlaskClient client: The client to run the test with.
    :param AuthActions auth: The authentication object to use for login.
    """
    auth.login()

    with client:
        Config.set_camera_info(CAMERA_NAME, True)

        response = client.get('/cameras/?name=' + CAMERA_NAME + '&action=delete',
                              follow_redirects=True)

        assert response.status_code == HTTPStatus.OK
        assert CAMERA_NAME.encode() not in response.data
        assert CAMERA_NAME not in Config.get_connected_cameras()
