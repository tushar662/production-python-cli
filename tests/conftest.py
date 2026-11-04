from collections.abc import Iterator
from pathlib import Path

import pytest

from task_manager.database import Database


@pytest.fixture
def database(tmp_path: Path) -> Iterator[Database]:
    """Provide a fresh, initialized SQLite database for each test."""
    db_path = tmp_path / "test_tasks.db"
    test_database = Database(str(db_path))
    test_database.create_tables()
    yield test_database
