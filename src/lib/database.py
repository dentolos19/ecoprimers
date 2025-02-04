import os

from flask import Flask
from flask import session as flask_session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from lib.models import Base, Event, Product, User

initialized: bool = False
sql: SQLAlchemy = None
session: Session = None


def init(app: Flask, local: bool = True):
    global initialized
    global sql
    global session

    # Skip if database session is already initialized
    if initialized:
        return

    first_setup = False

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

        # Check if the database file exists
        if not os.path.exists(database_file):
            first_setup = True

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
        # Create all the tables of the database; does not update existing tables
        with app.app_context():
            sql.create_all()

        initialized = True

        # Setup the database with initial data
        if first_setup:
            setup()


def setup():
    from main import app

    global sql

    with app.app_context():
        # Users
        sql.session.add(
            User(
                name="Administrator",
                email="admin@ecoprimers.app",
                password=generate_password_hash("admin", method="pbkdf2:sha1"),
            )
        )
        sql.session.add(
            User(
                name="Dennise Duck",
                email="dennise@duck.com",
                password=generate_password_hash("Dennise!123", method="pbkdf2:sha1"),
            )
        )

        # Events
        sql.session.add(Event(title="Cleaning Day", description="Todo", location="Chinatown", date="2025-03-01"))

        # Products
        sql.session.add(Product(name="Reusable Cup", points=200, stock=50, image_url="/static/img/reusable-cup.png"))
        sql.session.add(Product(name="Iron on Badge", points=100, stock=50, image_url="/static/img/iron_on.png"))
        sql.session.add(Product(name="Reusable Utensil", points=1000, stock=50, image_url="/static/img/reusable-utensil.png"))
        sql.session.add(Product(name="ZipLog Bag", points=500, stock=50, image_url="/static/img/ziplog-bag.png"))
        sql.session.add(Product(name="Notebook", points=1500, stock=50, image_url="/static/img/notebook.png"))
        sql.session.add(Product(name="Tote Bag", points=2000, stock=50, image_url="/static/img/tote_bag.png"))

        sql.session.commit()


def reset():
    from main import app

    global sql

    with app.app_context():
        sql.drop_all()
        sql.create_all()

    # Clears the current session; logs out the current user
    flask_session.clear()