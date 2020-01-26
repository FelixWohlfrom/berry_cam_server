import os
import shutil
import stat
import tempfile

import pytest

import berry_cam_server
from berry_cam_server import create_app, Config


def test_init():
    """
    Test creation of the flask application succeeds
    """
    # Make sure we have a valid configuration file
    Config.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf.yaml')
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_upload_dir_creation_absolute():
    """
    Verifies that upload dirs can be successfully created if they do not exist. Upload dir is an absolute path.
    """
    # Create a temporary directory and delete it directly to be sure it doesn't exist in the next step
    with tempfile.TemporaryDirectory() as upload_dir:
        tmpdir = upload_dir

    # Create app with temporary directory
    try:
        app = create_app({
            'TESTING': True,
            'UPLOAD_DIR': tmpdir
        })
        assert app
        assert os.path.exists(tmpdir)

    # Cleanup the directory
    finally:
        shutil.rmtree(tmpdir)


def test_upload_dir_creation_relative():
    """
    Verifies that upload dirs can be successfully created if they do not exist. Upload dir is a relative path.
    """
    testdir = os.path.join(os.path.dirname(berry_cam_server.__file__), 'test_uploads')
    assert not os.path.exists(testdir)

    # Create app with relative path
    try:
        app = create_app({
            'TESTING': True,
            'UPLOAD_DIR': 'test_uploads'
        })
        assert app
        assert os.path.exists(testdir)

    # Cleanup the directory
    finally:
        shutil.rmtree(testdir)


@pytest.mark.parametrize('directory', (
        'previews', 'raw',
))
def test_upload_dirs_write_protected(directory):
    """
    Verifies that upload dir checks fail if any upload dir is write protected
    """
    with tempfile.TemporaryDirectory() as upload_dir:
        testdir = os.path.join(upload_dir, directory)
        os.mkdir(testdir)
        os.chmod(testdir, stat.S_IREAD)

        with pytest.raises(SystemExit) as expected_exit:
            # This should fail
            create_app({
                'TESTING': True,
                'UPLOAD_DIR': upload_dir
            })

        assert expected_exit.type == SystemExit
        assert expected_exit.value.code == 1
