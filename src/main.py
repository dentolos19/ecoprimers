# The app folder was removed and the code was restructured to help with sqlite implementation.

import os

from flask import Flask

from models import db

app = Flask(__name__)

# Setup the local database folder
DATABASE_PATH = os.path.join(app.root_path, "data.db")
# Ensure that the directory for the database file exists
if not os.path.exists(os.path.dirname(DATABASE_PATH)):
    os.makedirs(os.path.dirname(DATABASE_PATH))

# Initialize app configurations
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret-key"

# Initialize app's database
db.init_app(app)
with app.app_context():
    # Ensure all tables are created before adding any data
    db.create_all()


# Import routes into the main module
from routes import *  # noqa: E402, F403

if __name__ == "__main__":
    app.run()