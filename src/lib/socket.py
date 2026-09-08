from typing import cast

from flask import Flask
from flask_socketio import SocketIO

initialized: bool = False
io = cast(SocketIO, None)


def init(app: Flask):
    global initialized
    global io

    if initialized:
        return

    io = SocketIO(app)
    io.init_app(app)

    initialized = True
