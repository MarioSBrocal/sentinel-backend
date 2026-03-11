from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every model in the application (e.g., User, Monitor) MUST inherit from this class.
    Alembic will inspect `Base.metadata` to auto-generate database migrations.
    """

    pass
