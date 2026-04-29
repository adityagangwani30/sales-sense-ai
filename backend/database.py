from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from database_loader import connect_db


@contextmanager
def get_connection() -> Iterator[object]:
    """Open one MySQL connection per request and close it afterward."""
    connection = connect_db()
    try:
        yield connection
    finally:
        connection.close()
