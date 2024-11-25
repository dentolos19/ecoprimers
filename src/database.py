import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from environment import TURSO_AUTH_TOKEN, TURSO_DATABASE_URL
from models import Base

session: Session = None


def init(local: bool = True):
    global session

    if local:
        # Setup the local database folder
        DATABASE_PATH = os.path.join(os.getcwd(), "data.db")
        # Ensure that the directory for the database file exists
        if not os.path.exists(os.path.dirname(DATABASE_PATH)):
            os.makedirs(os.path.dirname(DATABASE_PATH))
        url = "sqlite:///" + DATABASE_PATH
    else:
        url = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"  # noqa: F821

    try:
        # Create the database engine
        engine = create_engine(
            url, connect_args={"check_same_thread": False}, echo=True
        )
        session = Session(engine)  # noqa: F841
    except:  # noqa: E722
        # Uses local database if the remote database is not available
        init(local=True)
    else:
        Base.metadata.create_all(engine)