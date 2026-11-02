
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from task_manager.models import Task


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info("Database initialized: %s", db_path)

    def connect(self) -> sqlite3.Connection:
        logger.debug("Opening database connection")
        return sqlite3.connect(self.db_path)

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()

        try:
            yield connection
            connection.commit()
            logger.debug("Database transaction committed")

        except Exception:
            connection.rollback()
            logger.exception("Database transaction failed")
            raise

        finally:
            connection.close()
            logger.debug("Database connection closed")

    def create_tables(self) -> None:
        with self.get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

        logger.info("Tasks table created or already exists")

    def add_task(self, task: Task) -> int:
        with self.get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, completed, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    task.title,
                    int(task.completed),
                    task.created_at.isoformat(),
                ),
            )

            task_id = cursor.lastrowid

        logger.info("Task created successfully: ID %s", task_id)
        return task_id

    def get_tasks(self) -> list[Task]:
        with self.get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, title, completed, created_at
                FROM tasks
                ORDER BY id
                """
            )

            rows = cursor.fetchall()

            tasks = []

            for row in rows:
                task = Task(
                    title=row[1],
                    completed=bool(row[2]),
                    created_at=datetime.fromisoformat(row[3]),
                    id=row[0],
                )

                tasks.append(task)

        logger.info("Retrieved %s tasks", len(tasks))
        return tasks

    def complete_task(self, task_id: int) -> None:
        with self.get_connection() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET completed = 1
                WHERE id = ?
                """,
                (task_id,),
            )

        logger.info("Task marked completed: ID %s", task_id)

    def delete_task(self, task_id: int) -> None:
        with self.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            )

        logger.info("Task deleted: ID %s", task_id)
