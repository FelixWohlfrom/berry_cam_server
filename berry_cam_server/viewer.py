import os
import shutil
from datetime import datetime, timezone

from flask import Blueprint, render_template, current_app, send_from_directory, request, redirect

from .auth import login_required

bp = Blueprint('viewer', __name__)


@bp.route('/')
@login_required
def index():
    """
    If the user is logged in, it will show the most recent and older files that where uploaded to the viewer.

    :return: Rendered template
    :rtype: str
    """
    if request.args.get('cleanup') == 'true':
        shutil.rmtree(os.path.join(current_app.config["UPLOAD_DIR"], 'raw'))
        os.mkdir(os.path.join(current_app.config["UPLOAD_DIR"], 'raw'))
        shutil.rmtree(os.path.join(current_app.config["UPLOAD_DIR"], 'previews'))
        os.mkdir(os.path.join(current_app.config["UPLOAD_DIR"], 'previews'))
        return redirect('./')

    most_recent = []
    older = []
    for preview in sorted(os.listdir(os.path.join(current_app.config["UPLOAD_DIR"], "previews")), reverse=True):
        timestamp = str(preview.rsplit('.')[0])

        raw_file_without_ext = os.path.join(current_app.config["UPLOAD_DIR"], "raw", timestamp)
        if os.path.exists(raw_file_without_ext + ".jpg"):
            raw_file = timestamp + ".jpg"
        else:
            raw_file = timestamp + ".png"

        image_info = {
            "preview": preview,
            "rawfile": raw_file,
            "timestamp": datetime.fromtimestamp(float(timestamp) / 100, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }

        if len(most_recent) < 5:
            most_recent.append(image_info)
        else:
            older.append(image_info)

    return render_template('viewer.html', most_recent_pictures=most_recent, older_pictures=older)


@bp.route('/large/<path:path>')
@login_required
def large(path):
    """
    Will return raw images from raw directory. Checks for login.

    :param path: The image to load.
    :return: The file.
    :rtype: Any
    """
    return send_from_directory(os.path.join(current_app.config["UPLOAD_DIR"], 'raw'), path)


@bp.route('/previews/<path:path>')
@login_required
def previews(path):
    """
    Will return preview images from previews directory. Checks for login.

    :param path: The image to load.
    :return: The file.
    :rtype: Any
    """
    return send_from_directory(os.path.join(current_app.config["UPLOAD_DIR"], 'previews'), path)
