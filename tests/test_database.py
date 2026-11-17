import sqlite3

import pytest

from task_manager.database import Database
from task_manager.models import Task


def test_create_tables_initializes_tasks_table(database: Database) -> None:
    # Calling this twice also checks that initialization is safe to repeat.
    database.create_tables()

    with database.get_connection() as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
            ("table", "tasks"),
        ).fetchone()

    assert table == ("tasks",)


def test_get_tasks_returns_empty_list_for_new_database(database: Database) -> None:
    assert database.get_tasks() == []


def test_add_task_returns_id_and_task_can_be_retrieved(database: Database) -> None:
    task = Task(title="Write a unit test")

    task_id = database.add_task(task)
    retrieved_tasks = database.get_tasks()

    assert task_id == 1
    assert len(retrieved_tasks) == 1
    assert retrieved_tasks[0].id == task_id
    assert retrieved_tasks[0].title == task.title
    assert retrieved_tasks[0].completed is False
    assert retrieved_tasks[0].created_at == task.created_at


def test_add_task_preserves_completed_status(database: Database) -> None:
    task = Task(title="Already done", completed=True)

    task_id = database.add_task(task)
    retrieved_task = database.get_tasks()[0]

    assert retrieved_task.id == task_id
    assert retrieved_task.completed is True


def test_complete_task_marks_task_completed(database: Database) -> None:
    task_id = database.add_task(Task(title="Finish tests"))

    assert database.complete_task(task_id) is True

    retrieved_task = database.get_tasks()[0]
    assert retrieved_task.id == task_id
    assert retrieved_task.completed is True


def test_delete_task_removes_task(database: Database) -> None:
    task_id = database.add_task(Task(title="Remove this task"))

    assert database.delete_task(task_id) is True

    assert database.get_tasks() == []


def test_get_tasks_returns_tasks_in_id_order(database: Database) -> None:
    first_id = database.add_task(Task(title="First"))
    second_id = database.add_task(Task(title="Second"))

    tasks = database.get_tasks()

    assert [task.id for task in tasks] == [first_id, second_id]
    assert [task.title for task in tasks] == ["First", "Second"]


def test_completing_nonexistent_id_does_not_change_tasks(database: Database) -> None:
    task_id = database.add_task(Task(title="Keep this task"))
    before = database.get_tasks()

    assert database.complete_task(task_id + 100) is False

    assert database.get_tasks() == before


def test_deleting_nonexistent_id_does_not_change_tasks(database: Database) -> None:
    task_id = database.add_task(Task(title="Keep this task"))
    before = database.get_tasks()

    assert database.delete_task(task_id + 100) is False

    assert database.get_tasks() == before


def test_get_connection_rolls_back_and_reraises_exception(
    database: Database,
) -> None:
    with pytest.raises(RuntimeError, match="force rollback"):
        with database.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO tasks (title, completed, created_at)
                VALUES (?, ?, ?)
                """,
                ("This should be rolled back", 0, "2025-01-01T00:00:00"),
            )
            raise RuntimeError("force rollback")

    assert database.get_tasks() == []


def test_get_connection_closes_connection(database: Database) -> None:
    with database.get_connection() as connection:
        connection.execute("SELECT 1")

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_get_connection_closes_connection_after_exception(
    database: Database,
) -> None:
    with pytest.raises(RuntimeError, match="force close"):
        with database.get_connection() as connection:
            raise RuntimeError("force close")

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")
