from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect

from .auth import login_required
from .common.conf import Config

bp = Blueprint('cameras', __name__, url_prefix='/cameras')


@bp.route('/')
@login_required
def index():
    """
    Displays the camera information.

    :return: The html
    :rtype: str
    """
    connected_cameras = {}

    if request.args.get('name'):
        if request.args.get('enable', None) is not None:
            if request.args.get('enable') == 'true':
                Config.enable_camera(request.args.get('name'), True)
            else:
                Config.enable_camera(request.args.get('name'), False)

        if request.args.get('action') == 'delete':
            Config.remove_camera(request.args.get('name'))
            return redirect('./')

    for name, camera in Config.get_connected_cameras().items():
        current_timestamp = datetime.now(tz=timezone.utc)
        last_connection = datetime.fromtimestamp(float(camera['last_connection']), tz=timezone.utc)
        camera['last_connection'] = \
            last_connection.strftime('%Y-%m-%d %H:%M:%S UTC')
        camera['last_connection_pending'] = (current_timestamp - last_connection).seconds > 300
        connected_cameras[name] = camera

    return render_template('cameras.html', cameras=connected_cameras)
