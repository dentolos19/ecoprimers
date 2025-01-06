import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from environment import TURSO_AUTH_TOKEN, TURSO_DATABASE_URL
from models import Base

session: Session = None


def init(local: bool = True):
    global session

    # Skip if database session is already initialized
    if session:
        return

    if local:
        # Setup the local database folder
        database_dir = os.getcwd()
        database_file = os.path.join(database_dir, "data.db")

        # Ensure that the directory for the database exists
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
        url = "sqlite:///" + database_file
    else:
        url = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

    try:
        # Create the database engine
        engine = create_engine(
            url, connect_args={"check_same_thread": False}, echo=True
        )
        session = Session(engine)
    except:
        # Uses local database if the remote database is not available
        init(local=True)
    else:
        Base.metadata.create_all(engine)