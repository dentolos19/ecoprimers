from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from lib.database import get_url

load_dotenv()

seed_file = Path(__file__).resolve().parents[1] / "seed.sql"
statements = [statement.strip() for statement in seed_file.read_text().split(";") if statement.strip()]

with create_engine(get_url()).begin() as connection:
    for statement in statements:
        connection.execute(text(statement))
