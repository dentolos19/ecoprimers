import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base

TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

database: Session = None


def init(local: bool = True):
    global database

    if local:
        # Setup the local database folder
        DATABASE_PATH = os.path.join(os.getcwd(), "data.db")
        # Ensure that the directory for the database file exists
        if not os.path.exists(os.path.dirname(DATABASE_PATH)):
            os.makedirs(os.path.dirname(DATABASE_PATH))
        url = "sqlite:///" + DATABASE_PATH
    else:
        url = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

    # Create the database engine
    try:
        engine = create_engine(url, connect_args={"check_same_thread": False}, echo=True)
        database = Session(engine)  # noqa: F841
    except:  # noqa: E722
        init(local=True)
    else:
        Base.metadata.create_all(engine)