"""Initialize the database tables defined by the ORM models."""

from backend.app.database import engine
from backend.app.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()