import os
from datetime import datetime, timezone
from http import HTTPStatus

from PIL import Image
from flask import current_app
from flask_restx import Resource, Namespace, abort
from werkzeug.datastructures import FileStorage

from berry_cam_server import auth

api = Namespace('picture', description='Api endpoints to interact with the pictures stored in the server.')

upload_parser = auth.api_key_parser.copy()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, help="The picture to upload.", required=True)


@api.route('/')
@api.expect(auth.api_key_parser)
class Pictures(Resource):
    """
    Handler class for picture related REST Api.
    """

    @api.doc(responses={200: 'Success',
                        400: 'Invalid file types',
                        429: 'On too many requests',
                        403: 'On invalid API key',
                        500: 'On errors while creating thumbnails.'})
    @auth.api_key_required
    @api.expect(upload_parser)
    def post(self):
        """
        Will store the given image with current utc unix timestamp as file name.
        Maximum one request per second allowed.

        :return: "Success" on success
        :rtype: str
        """
        # This will also check that mandatory file key is available in arguments and stop execution if not.
        args = upload_parser.parse_args()

        if args.file.content_type not in ['image/png', 'image/jpeg']:
            abort(HTTPStatus.BAD_REQUEST,
                  "Invalid file type given. Only images allowed. Given file type: {}".format(args.file.content_type))

        filename = int(datetime.now(timezone.utc).timestamp() * 100)
        extension = 'png' if args.file.content_type == 'image/png' else 'jpg'
        raw_image = os.path.join(current_app.config["UPLOAD_DIR"], "raw", "{}.{}".format(filename, extension))

        if os.path.exists(raw_image):
            abort(HTTPStatus.TOO_MANY_REQUESTS, "Please don't spam the server and reduce image upload frequency.")

        args.file.save(raw_image)

        try:
            with Image.open(args.file.stream) as thumbnail:
                thumbnail.thumbnail((128, 128))
                thumbnail.save(
                    os.path.join(current_app.config["UPLOAD_DIR"], "previews", "{}.jpg".format(filename)), "JPEG")
        except IOError:
            os.remove(raw_image)
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, "Could not create thumbnail")

        return "Success"
