from flask import Flask

app = Flask(__name__)

# Do not remove this, the routes will be imported here
from app.routes import *  # noqa: E402, F403