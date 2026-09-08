import io
from collections.abc import Collection

from flask import Flask, abort, send_file
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from lib import database
from lib.models import Asset

image_extensions = {"png", "jpg", "jpeg", "gif"}
video_extensions = {"mp4"}
media_extensions = image_extensions.union(video_extensions)

initialized: bool = False


def init(app: Flask):
    global initialized

    if initialized:
        return

    app.add_url_rule("/assets/<asset_id>", "asset", get_asset)

    initialized = True


def check_format(file: FileStorage, allowed_extensions: Collection[str]) -> bool:
    filename = file.filename or ""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def upload_asset(file: FileStorage) -> str:
    name = secure_filename(file.filename or "")
    asset = Asset(
        content_type=file.mimetype or "application/octet-stream",
        data=file.read(),
        name=name or "upload",
    )
    database.session.add(asset)
    database.session.commit()
    return f"/assets/{asset.id}"


def get_asset(asset_id: str):
    asset = database.session.get(Asset, asset_id)
    if asset is None:
        abort(404)
    return send_file(
        io.BytesIO(asset.data),
        download_name=asset.name,
        max_age=31536000,
        mimetype=asset.content_type,
    )
