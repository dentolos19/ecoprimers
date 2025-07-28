import os

import sentry_sdk
from flask import Flask

from lib import ai, database, google, payments, socket, storage
from lib.socket import io as socketio
from utils import load_environment

# Load environment variables
load_environment()

# Initialize Sentry monitoring
sentry_sdk.init(
    dsn="https://a9f0e36f0f4211d6ae869a69fbf94d1a@o4509741698121728.ingest.us.sentry.io/4509741698383872",
    send_default_pii=True,
)

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app_debug = app.config["DEBUG"]

# Initialize internal systems
database.init(app, local=app_debug)
storage.init(app, local=app_debug)
ai.init(app)
payments.init(app)
google.init(app)
socket.init(app)

# Import routes into the main module
from routes import *

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=app_debug, allow_unsafe_werkzeug=True)