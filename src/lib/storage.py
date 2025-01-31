import os

from flask import Flask

initialized: bool = False


def init(app: Flask):
    global initialized

    if initialized:
        return

    app.config["UPLOAD_FOLDER"] = "src/static/uploads"

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    initialized = True