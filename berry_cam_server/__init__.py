import logging
import os

from flask import Flask

from .common.conf import Config

LOG = logging.getLogger(__name__)


def check_upload_dir(app):
    """
    Will check if the uplaod directory for a given flask app exists.

    :param Flask app: The flask app to check the upload dir for.
    """

    if "UPLOAD_DIR" in app.config:
        upload_dir = app.config["UPLOAD_DIR"]
        if not upload_dir.startswith('/'):
            upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), upload_dir))
    else:
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')

    app.config["UPLOAD_DIR"] = upload_dir

    if not os.path.exists(upload_dir):
        LOG.info("Image upload directory %s does not exist. Creating it.", upload_dir)
        os.makedirs(upload_dir)

    previews_dir = os.path.join(upload_dir, 'previews')
    if not os.path.exists(previews_dir):
        LOG.info("Previews directory %s does not exist. Creating it.", previews_dir)
        os.makedirs(previews_dir)

    raw_dir = os.path.join(upload_dir, 'raw')
    if not os.path.exists(raw_dir):
        LOG.info("Raw image directory %s does not exist. Creating it.", raw_dir)
        os.makedirs(raw_dir)

    if not os.access(previews_dir, os.W_OK):
        LOG.fatal("Previews directory %s is not writable.", previews_dir)
        exit(1)

    if not os.access(raw_dir, os.W_OK):
        LOG.fatal("Raw image directory %s is not writable.", raw_dir)
        exit(1)

    LOG.info("Using image upload dir: %s", upload_dir)


def create_app(test_config=None):
    """
    Creates a new flask application.

    :param test_config: The test configuration to use. Leave empty for prod mode.
    :return: A flask application
    :rtype: Flask
    """

    logging.basicConfig(level=logging.INFO)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    else:
        # load the real server config
        app.config.from_mapping(Config.get_server_config())

    # Check if upload dir exists and is writable
    check_upload_dir(app)

    # Api initialisation
    from .api import blueprint as api
    app.register_blueprint(api)

    # User frontend initialisation
    from . import auth
    app.register_blueprint(auth.bp)
    from . import api_key
    app.register_blueprint(api_key.bp)
    from . import cameras
    app.register_blueprint(cameras.bp)

    from . import viewer
    app.register_blueprint(viewer.bp)
    app.add_url_rule('/', endpoint='index')

    return app
