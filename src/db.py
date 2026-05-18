from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def make_engine(connection_url: str) -> Engine:
    return create_engine(connection_url, future=True)

