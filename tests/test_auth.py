from http import HTTPStatus

import pytest
from flask import g, session


def test_login_success(client, auth):
    """
    Verifies that the login is successful with valid credentials.

    :param FlaskClient client: The client to use for the connection.
    :param AuthActions auth: The authentication module to simulate authentication.
    """
    assert client.get('/auth/login').status_code == HTTPStatus.OK
    auth.login()

    with client:
        client.get('/')
        assert session['username'] == 'test'
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password'), (
        ('foo', 'test'),
        ('test', 'foo'),
))
def test_login_failures(auth, username, password):
    """
    Verifies that login fails in invalid username or password.

    :param AuthActions auth: The authentication object to run the test on
    :param str username: The username to test
    :param str password: The password to test
    """
    response = auth.login(username, password)
    assert b'Invalid credentials' in response.data


def test_logout(client, auth):
    """
    Verifies that logout works fine.

    :param FlaskClient client: The client to use for logout.
    :param AuthActions auth: The authentication object to logout with.
    """
    auth.login()

    with client:
        auth.logout()
        assert 'username' not in session
