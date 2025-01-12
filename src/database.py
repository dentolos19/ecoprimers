import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

from models import Base

initialized: bool = False
sql: SQLAlchemy = None
session: Session = None
migrate: Migrate = None


def init(app: Flask, local: bool = True):
    global initialized
    global sql
    global session
    global migrate

    # Skip if database session is already initialized
    if initialized:
        return

    # Load environment variables
    app.config["TURSO_DATABASE_URL"] = os.environ.get("TURSO_DATABASE_URL")
    app.config["TURSO_AUTH_TOKEN"] = os.environ.get("TURSO_AUTH_TOKEN")

    if local:
        # Setup the local database folder
        database_dir = os.getcwd()
        database_file = os.path.join(database_dir, "data.db")

        # Ensure that the directory for the database exists
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
        url = "sqlite:///" + database_file
    else:
        url = f"sqlite+{app.config['TURSO_DATABASE_URL']}/?authToken={app.config['TURSO_AUTH_TOKEN']}&secure=true"

    # Set the database environment
    app.config["SQLALCHEMY_DATABASE_URI"] = url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    try:
        sql = SQLAlchemy(model_class=Base)
        session = sql.session

        # Initialize the app with the extension
        sql.init_app(app)
    except:
        # Uses local database if the remote database is not available
        init(app, local=True)
    else:
        # Automatically update the database schema to match the models
        with app.app_context():
            sql.create_all()

        migrate = Migrate(app, sql)

        initialized = True