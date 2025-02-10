import os

from flask import Flask
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

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


def upload(file: FileStorage) -> str:
    from main import app
    from utils import generate_random_string

    name = secure_filename(file.filename)
    generated_name = generate_random_string()

    if "." in name:
        generated_name += name[name.rindex(".") :]

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], generated_name))
    return "/static/uploads/" + generated_name