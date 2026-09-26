import sqlite3
from datetime import datetime

from task_manager.models import Task


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        connection = self.connect()

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def add_task(self, task: Task) -> int:
     with self.connect() as connection:
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

        return cursor.lastrowid

    def get_tasks(self) -> list[Task]:
        connection = self.connect()

        cursor = connection.execute(
            """
            SELECT id, title, completed, created_at
            FROM tasks
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

        connection.close()

        tasks = []

        for row in rows:
            task = Task(
                title=row[1],
                completed=bool(row[2]),
                created_at=datetime.fromisoformat(row[3]),
                id=row[0],
            )

            tasks.append(task)

        return tasks

    def complete_task(self, task_id: int) -> None:
        connection = self.connect()

        connection.execute(
            """
            UPDATE tasks
            SET completed = 1
            WHERE id = ?
            """,
            (task_id,),
        )

        connection.commit()
        connection.close()

    def delete_task(self, task_id: int) -> None:
        connection = self.connect()

        connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        connection.commit()
        connection.close()