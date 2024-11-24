from flask import Flask

import database

app = Flask(__name__)

# Initialize app's database
database.init(local=False)

# Import routes into the main module
from routes import *  # noqa: E402, F403

if __name__ == "__main__":
    app.run()