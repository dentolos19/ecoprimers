import os

from flask import Flask
from flask_socketio import SocketIO

from lib import ai, database, google, payments, storage

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

socket = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Setup global variables
app_debug = bool(app.config["DEBUG"])

# Initialize internal systems
ai.init(app)
database.init(app, local=app_debug)
google.init(app)
payments.init(app)
storage.init(app)

# Import routes into the main module
from routes import *

if __name__ == "__main__":
    socket.run(app, host="127.0.0.1", port=5000, debug=app_debug)
    app.run(host="127.0.0.1", port=3000)