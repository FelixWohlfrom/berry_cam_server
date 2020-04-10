from http import HTTPStatus

import pytest

from berry_cam_server import Config


def test_get_missing_api_key(client):
    """
    Verifies that the correct error message is shown on missing api key during get requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.get('/api/camera/')

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'missing' in response.data.lower() and b'api_key' in response.data


def test_get_data_invalid_api_key(client):
    """
    Verifies that the correct error message is shown if an invalid api key is given for get requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.get('/api/camera/', data={'api_key': 'invalid'})

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert b'invalid' in response.data.lower() and b'api_key' in response.data


def test_get_missing_name(client):
    """
    Verifies that the correct error message is shown if camera name is missing for get requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.get(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key']})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'name' in response.data.lower()
        assert b'camera' in response.data.lower()
        assert b'missing' in response.data.lower()


def test_get_unknown_camera(client):
    """
    Verifies that the correct error message is shown if an unknown camera should be requested.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.get(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': 'Unknown_Camera'})

        assert response.status_code == HTTPStatus.OK
        assert response.json['enabled'] == False  # The 'should' state sent by the server


def test_post_missing_api_key(client):
    """
    Verifies that the correct error message is shown on missing api key during post requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/camera/')

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'missing' in response.data.lower() and b'api_key' in response.data


def test_post_data_invalid_api_key(client):
    """
    Verifies that the correct error message is shown if an invalid api key is given for post requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/camera/', data={'api_key': 'invalid'})

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert b'invalid' in response.data.lower() and b'api_key' in response.data


def test_post_missing_name(client):
    """
    Verifies that the correct error message is shown if camera name is missing for post requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/camera/',
                               data={'api_key': Config.get_user_config('test')['api_key']})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'name' in response.data.lower()
        assert b'camera' in response.data.lower()
        assert b'missing' in response.data.lower()


def test_post_missing_enabled_state(client):
    """
    Verifies that the correct error message is shown if camera enabled state is missing for post requests.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/camera/',
                               data={'api_key': Config.get_user_config('test')['api_key'],
                                     'name': 'Test-Camera'})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'camera' in response.data.lower()
        assert b'enabled' in response.data.lower()
        assert b'missing' in response.data.lower()


@pytest.mark.parametrize('enabled', (
    'false', 'False', 'true', 'True',
))
def test_set_camera_data(client, enabled):
    """
    Verifies that setting the enabled state of the camera sets the state correctly.

    :param FlaskClient client: The flask client to use for the test.
    :param str enabled: The camera enabled state
    """

    camera_name = 'Test-Camera'
    expected_enabled = enabled in ('true', 'True')

    with client:
        response = client.post(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': camera_name,
                                  'enabled': enabled})

        assert response.status_code == HTTPStatus.OK

        response = client.get(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': camera_name})

        assert response.status_code == HTTPStatus.OK
        assert response.json['camera_enabled'] == expected_enabled  # The current state of the camera


def test_update_camera_data(client):
    """
    Verifies that updating the camera data for a single camera updates the data correctly.

    :param FlaskClient client: The flask client to use for the test.
    """

    camera_name = 'Test-Camera'

    with client:
        response = client.post(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': camera_name,
                                  'enabled': False})

        assert response.status_code == HTTPStatus.OK
        assert Config.get_connected_cameras()[camera_name]['camera_enabled'] == False

        response = client.post(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': camera_name,
                                  'enabled': True})

        assert response.status_code == HTTPStatus.OK
        assert Config.get_connected_cameras()[camera_name]['camera_enabled'] == True


def test_post_two_camera_names(client):
    """
    Verifies that posting two different camera names works also fine and that two cameras are then stored
    in config.

    :param FlaskClient client: The flask client to use for the test.
    """
    with client:
        response = client.post(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': 'Camera1',
                                  'enabled': True})

        assert response.status_code == HTTPStatus.OK

        response = client.post(
            '/api/camera/', data={'api_key': Config.get_user_config('test')['api_key'],
                                  'name': 'Camera2',
                                  'enabled': True})

        assert response.status_code == HTTPStatus.OK

        assert len(Config.get_connected_cameras()) == 2