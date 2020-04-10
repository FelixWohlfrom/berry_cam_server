from flask_restx import Resource, Namespace

from berry_cam_server import auth, Config

api = Namespace('camera', description='Api endpoints to send camera infos to the server and fetch configurations.')

camera_name_parser = auth.api_key_parser.copy()
camera_name_parser.add_argument('name', type=str, help="The name of the camera.", required=True)

camera_enabled_parser = camera_name_parser.copy()
camera_enabled_parser.add_argument('enabled', type=str, help="If the camera is enabled or not", required=True)


@api.route('/')
@api.expect(auth.api_key_parser)
class Camera(Resource):
    """
    Handler class for camera related REST Api.
    """
    ALIVE_QUEUE = None

    @api.doc(responses={200: 'OK', 403: 'On invalid API key'})
    @auth.api_key_required
    @api.expect(camera_name_parser)
    def get(self):
        # This will also check that mandatory file key is available in arguments and stop execution if not.
        args = camera_name_parser.parse_args()

        cameras = Config.get_connected_cameras()
        if args.name in cameras:
            return cameras[args.name]

        return {
            "enabled": False
        }

    @api.doc(responses={200: 'OK', 403: 'On invalid API key'})
    @auth.api_key_required
    @api.expect(camera_enabled_parser)
    def post(self):
        """
        :return: "Success" on success
        :rtype: str
        """
        # This will also check that mandatory file key is available in arguments and stop execution if not.
        args = camera_enabled_parser.parse_args()

        Config.set_camera_info(args.name, args.enabled in ("true", "True"))
        return "Success"
