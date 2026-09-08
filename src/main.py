import os

from flask import Flask

from lib import ai, database, google, socket, storage
from lib.socket import io as socketio
from utils import load_environment

# Load environment variables
load_environment()

# Initialize Flask app
app = Flask(__name__, static_folder="../public", static_url_path="/static", template_folder="../templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app_debug = app.config["DEBUG"]

# Initialize internal systems
database.init(app)
storage.init(app)
ai.init(app)
google.init(app)
socket.init(app)

# Import routes into the main module
from routes import *  # noqa: E402,F403

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3000, debug=app_debug, allow_unsafe_werkzeug=True)
