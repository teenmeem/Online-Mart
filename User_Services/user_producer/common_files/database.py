from contextlib import contextmanager
from sqlmodel import Session, SQLModel, create_engine
from . import settings

# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# recycle connections after 5 minutes
# to correspond with the compute scale down
# engine = create_engine(
#    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300)

# Also change in .env file


@contextmanager
def get_session():
    """
    A function that returns a session object using the provided engine.
    """
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """
    Function to create the database and its tables.
    """
    SQLModel.metadata.create_all(engine)
