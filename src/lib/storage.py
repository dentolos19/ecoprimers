import os
import uuid
from collections.abc import Collection
from typing import Any

import boto3
from botocore.exceptions import ClientError
from flask import Flask, Response, abort, stream_with_context
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

image_extensions = {"png", "jpg", "jpeg", "gif"}
video_extensions = {"mp4"}
media_extensions = image_extensions.union(video_extensions)

bucket = "assets"
client: Any = None
initialized: bool = False


def init(app: Flask):
    global client, initialized

    if initialized:
        return

    client = boto3.client("s3", endpoint_url=os.environ.get("AWS_ENDPOINT_URL_S3"))
    app.add_url_rule("/assets/<asset_id>", "asset", get_asset)

    initialized = True


def check_format(file: FileStorage, allowed_extensions: Collection[str]) -> bool:
    filename = file.filename or ""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def upload_asset(file: FileStorage) -> str:
    name = secure_filename(file.filename or "")
    asset_id = str(uuid.uuid4())
    client.upload_fileobj(
        file.stream,
        bucket,
        asset_id,
        ExtraArgs={
            "CacheControl": "public, max-age=31536000, immutable",
            "ContentDisposition": f'inline; filename="{name or "upload"}"',
            "ContentType": file.mimetype or "application/octet-stream",
            "Metadata": {"name": name or "upload"},
        },
    )
    return f"/assets/{asset_id}"


def get_asset(asset_id: str):
    try:
        asset = client.get_object(Bucket=bucket, Key=asset_id)
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") in {"404", "NoSuchKey"}:
            abort(404)
        raise

    body = asset["Body"]
    response = Response(
        stream_with_context(body.iter_chunks()),
        content_type=asset.get("ContentType", "application/octet-stream"),
        headers={
            "Cache-Control": asset.get("CacheControl", "public, max-age=31536000, immutable"),
            "Content-Disposition": asset.get("ContentDisposition", "inline"),
        },
    )
    response.call_on_close(body.close)
    return response
