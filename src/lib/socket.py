from flask import Flask
from flask_socketio import SocketIO

initialized: bool = False
io: SocketIO = None


def init(app: Flask):
    global initialized
    global io

    if initialized:
        return

    io = SocketIO(app, async_mode="eventlet")
    io.init_app(app)

    initialized = True