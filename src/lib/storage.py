"""Remote S3 storage for uploaded assets."""

import os
import uuid
from collections.abc import Collection
from urllib.parse import urlsplit

from flask import Flask, Response, abort, g, stream_with_context
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

image_extensions = {"png", "jpg", "jpeg", "gif"}
video_extensions = {"mp4"}
media_extensions = image_extensions.union(video_extensions)
cache_control = "public, max-age=31536000, immutable"
BUCKET = "assets"


def init(app: Flask) -> None:
    app.add_url_rule("/assets/<asset_id>", "asset", get_asset)


def client():
    if "s3_client" not in g:
        from minio import Minio

        endpoint = urlsplit(os.environ.get("AWS_ENDPOINT_URL_S3") or "https://s3.amazonaws.com")
        g.s3_client = Minio(
            endpoint.netloc,
            access_key=os.environ.get("AWS_ACCESS_KEY_ID"),
            secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            secure=endpoint.scheme == "https",
            region=os.environ.get("AWS_REGION") or None,
        )
    return g.s3_client


def check_format(file: FileStorage, allowed_extensions: Collection[str]) -> bool:
    filename = file.filename or ""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def upload_asset(file: FileStorage) -> str:
    name = secure_filename(file.filename or "")
    asset_id = str(uuid.uuid4())
    file.stream.seek(0, os.SEEK_END)
    length = file.stream.tell()
    file.stream.seek(0)
    client().put_object(
        bucket_name=BUCKET,
        object_name=asset_id,
        data=file.stream,
        length=length,
        content_type=file.mimetype or "application/octet-stream",
        metadata={
            "Cache-Control": cache_control,
            "Content-Disposition": f'inline; filename="{name or "upload"}"',
            "X-Amz-Meta-Name": name or "upload",
        },
        num_parallel_uploads=1,
    )
    return f"/assets/{asset_id}"


def get_asset(asset_id: str):
    from minio.error import S3Error

    try:
        body = client().get_object(bucket_name=BUCKET, object_name=asset_id)
    except S3Error as error:
        if error.code == "NoSuchKey":
            abort(404)
        raise

    response = Response(
        stream_with_context(body.stream(32 * 1024)),
        content_type=body.headers.get("Content-Type", "application/octet-stream"),
        headers={
            "Cache-Control": body.headers.get("Cache-Control", cache_control),
            "Content-Disposition": body.headers.get("Content-Disposition", "inline"),
        },
    )

    def close_body():
        body.close()
        body.release_conn()

    response.call_on_close(close_body)
    return response
