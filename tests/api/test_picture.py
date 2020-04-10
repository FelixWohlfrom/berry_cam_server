import io
import os
from http import HTTPStatus
from concurrent.futures import ThreadPoolExecutor

import pytest

from berry_cam_server import Config


def test_upload_missing_api_key(client):
    """
    Verifies that the correct error message is shown on missing api key during image uploads.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/picture/')

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'missing' in response.data.lower() and b'api_key' in response.data


def test_upload_invalid_api_key(client):
    """
    Verifies that the correct error message is shown if an invalid api key is given.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/picture/', data={'api_key': 'invalid'})

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert b'invalid' in response.data.lower() and b'api_key' in response.data


def test_upload_missing_file(client):
    """
    Verifies that the correct error message is shown if the api key is valid, but the uploaded file is missing.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post(
            '/api/picture/', data={'api_key': Config.get_user_config('test')['api_key']})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'missing' in response.data.lower() and b'file' in response.data


def test_upload_invalid_file(client):
    """
    Verifies that the correct error message is shown if the api key is valid, but the uploaded file is of wrong type.

    :param FlaskClient client: The flask client to use for the test.
    """

    with client:
        response = client.post('/api/picture/', data={
            'api_key': Config.get_user_config('test')['api_key'],
            'file': (io.BytesIO(b"test"), 'test.txt')
        })

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b'invalid file type' in response.data.lower() and b'file' in response.data


def test_upload_thumbnail_creation_failure(client):
    """
    Test thumbnail creation with an invalid byte stream that is not a valid picture.
    The creation should fail.

    :param FlaskClient client: The flask client to use for the test.
    """
    with client:
        response = client.post('/api/picture/', data={
            'api_key': Config.get_user_config('test')['api_key'],
            'file': (io.BytesIO(b"test"), 'test.jpg')
        })

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert b'thumbnail' in response.data.lower()


@pytest.mark.parametrize('file_type', (
    'jpg', 'png',
))
def test_upload_valid_file(client, file_type):
    """
    Tests uploading of a valid jpg and png file. Both should succeed.

    :param FlaskClient client: The flask client to use for the test.
    :param str file_type: The file type to upload.
    """
    with client:
        test_file = os.path.join(os.path.dirname(
            __file__), 'test_data', 'test.{}'.format(file_type))
        response = client.post('/api/picture/', data={
            'api_key': Config.get_user_config('test')['api_key'],
            'file': (open(test_file, 'rb'), 'test.{}'.format(file_type))
        })

        assert response.status_code == HTTPStatus.OK
        assert response.data.decode('utf-8').strip() == '"Success"'


def run_upload_test(client):
    """
    Will execute the uploading of a single file and return the response.
    Used in test_upload_verify_fast.

    :param FlaskClient client: The flask client to use for the test.
    :returns: The upload response.
    """
    test_file = os.path.join(os.path.dirname(__file__),
                             'test_data', 'test.jpg')

    with open(test_file, 'rb') as bin_data:
        # First request should succeed
        response = client.post('/api/picture/', data={
            'api_key': Config.get_user_config('test')['api_key'],
            'file': (bin_data, 'test.jpg')
        })
        return response


def test_upload_very_fast(client):
    """
    This test tries to provoke a TOO_MANY_REQUEST response by firing a lot of
    parallel requests to the server. At least one of them should return a
    TOO_MANY_REQUESTS response.

    :param FlaskClient client: The flask client to use for the test.
    """
    with client:
        parallel_executions = 10
        with ThreadPoolExecutor(max_workers=parallel_executions) as pool:
            response = [None] * parallel_executions
            # Fire up a bunch of requests in parallel as fast as possible
            for i in range(parallel_executions):
                response[i] = pool.submit(run_upload_test, client)

            # Afterwards wait for the results and check them
            too_many_requests_found = False
            for i in range(parallel_executions):
                if response[i].result().status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    too_many_requests_found = True
                else:
                    assert response[i].result().status_code == HTTPStatus.OK

            assert too_many_requests_found
