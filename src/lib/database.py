import os

from flask import Flask
from flask import session as flask_session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

from lib.models import Base, Event, Product, Task

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
        url = f"sqlite+{app.config['TURSO_DATABASE_URL']}?/secure=true&authToken={app.config['TURSO_AUTH_TOKEN']}"

    # Set the database environment
    app.config["SQLALCHEMY_DATABASE_URI"] = url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    # Initialize the database extension
    sql = SQLAlchemy(model_class=Base)
    session = sql.session

    # Initialize the app with the extension
    sql.init_app(app)

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
        # Events
        sql.session.add(
            Event(
                title="Cleaning Day",
                description="Join us for a community cleaning day to help keep our neighborhood clean and green. All necessary cleaning supplies will be provided.",
                location="Yishun",
                date="2025-03-01",
                image_url="/static/img/cleaning-day.jpg",
            )
        )
        sql.session.add(
            Event(
                title="Newspaper Roll",
                description="Participate in our newspaper roll event where we collect and recycle old newspapers. Help us promote recycling and reduce waste.",
                location="Ang Mo Kio",
                date="2025-03-01",
                image_url="/static/img/newspaper-roll.jpg",
            )
        )

        # Tasks
        sql.session.add(
            Task(
                name="EcoWalkSnap",
                description="Step out for the planet! Take a walk, pick up litter, snap a photo, and upload it for AI verification. Keep your surroundings clean and beautiful!",
                criteria="A green space with no litter and very clean, or litter picked up and disposed of properly.",
                points=100,
                image_url="/static/img/first.png",
            )
        )
        sql.session.add(
            Task(
                name="RecycleVision",
                description="Collect recyclables, snap a picture as you drop them in the bin, and let AI verify your eco-friendly actions. Save reusable material and save the world!",
                criteria="Recyclables in a recycling bin, or recyclables being dropped into a recycling bin.",
                points=100,
                image_url="/static/img/vision.png",
            )
        )
        sql.session.add(
            Task(
                name="Thirsty Roots",
                description="Water a plant or tree, snap a picture, and let AI verify your care for nature. Help save your environment with your conscious effort.",
                criteria="A plant or tree being watered, or a plant or tree being watered with a watering can.",
                points=100,
                image_url="/static/img/thirstyroots.png",
            )
        )
        sql.session.add(
            Task(
                name="Lights Out",
                description="Turn off unused lights, snap a pic, and let AI confirm your energy-saving efforts. With your help we can save our environment.",
                criteria="A room with lights off, or a room with lights off and a person in the room.",
                points=100,
                image_url="/static/img/lights.png",
            )
        )

        # Products
        sql.session.add(
            Product(
                name="Reusable Cup",
                description="Made from durable materials, this reusable cup helps reduce single-use plastics and is perfect for your daily coffee needs!",
                points=200,
                stock=50,
                image_url="/static/img/reusable-cup.png",
            )
        )
        sql.session.add(
            Product(
                name="Iron on Badge",
                description="how your support for sustainability with this iron-on badge. Perfect for bags, jackets, or hats!",
                points=100,
                stock=50,
                image_url="/static/img/iron-on-badge.png",
            )
        )
        sql.session.add(
            Product(
                name="Reusable Utensil",
                description="Eco-friendly and reusable, this utensil set helps you reduce waste during meals.",
                points=1000,
                stock=50,
                image_url="/static/img/reusable-utensil.png",
            )
        )
        sql.session.add(
            Product(
                name="ZipLog Bag",
                description="Reusable and durable, this ZipLog bag is ideal for storing snacks or supplies!",
                points=500,
                stock=50,
                image_url="/static/img/ziplog-bag.png",
            )
        )
        sql.session.add(
            Product(
                name="Notebook",
                description="Stay organized with this eco-friendly notebook made from recycled materials.",
                points=1500,
                stock=50,
                image_url="/static/img/notebook.png",
            )
        )
        sql.session.add(
            Product(
                name="Tote Bag",
                description="Made from durable, reusable materials, this tote bag helps reduce plastic waste.",
                points=2000,
                stock=50,
                image_url="/static/img/tote-bag.png",
            )
        )

        sql.session.commit()


def reset():
    from main import app

    global sql

    with app.app_context():
        sql.drop_all()
        sql.create_all()

    # Clears the current session; logs out the current user
    flask_session.clear()