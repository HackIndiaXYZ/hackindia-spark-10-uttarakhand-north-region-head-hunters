"""Add the supporting event IDs column to the findings table."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)


def add_supporting_event_ids_column() -> None:
    """Add the nullable supporting event IDs column if it does not exist."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE findings "
                "ADD COLUMN IF NOT EXISTS supporting_event_ids JSON"
            )
        )
    print("Successfully ensured findings.supporting_event_ids exists.")


if __name__ == "__main__":
    add_supporting_event_ids_column()
