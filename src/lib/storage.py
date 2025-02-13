import os

from flask import Flask
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

image_extensions = {"png", "jpg", "jpeg", "gif"}
video_extensions = {"mp4"}
media_extensions = image_extensions.union(video_extensions)

initialized: bool = False


def init(app: Flask, local: bool = True):
    global initialized
    global session

    if initialized:
        return

    app.config["UPLOAD_FOLDER"] = "src/static/uploads"

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    initialized = True


def check_format(file: FileStorage, allowed_extensions: list[str]) -> bool:
    return "." in file.filename and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions


def upload_file(file: FileStorage) -> str:
    # TODO: Upload files to cloud

    return save_file(file).strip("src")


def save_file(file: FileStorage) -> str:
    from main import app
    from utils import generate_random_string

    name = secure_filename(file.filename)
    generated_name = generate_random_string()

    if "." in name:
        generated_name += name[name.rindex(".") :]

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], generated_name))
    return "src/static/uploads/" + generated_name