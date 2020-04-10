from flask import Blueprint
from flask_restx import Api

from .picture import api as picture_api
from .camera import api as camera_api

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(
    blueprint,
    title='BerryCam Server REST API',
    version='1.0',
    description='On this page you can find a description of the REST API for the BerryCam Server. '
                'See the different functions for detailed descriptions.'
)

api.add_namespace(picture_api)
api.add_namespace(camera_api)
