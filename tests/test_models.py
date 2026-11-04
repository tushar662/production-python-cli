from datetime import datetime

from task_manager.models import Task


def test_task_uses_default_values() -> None:
    task = Task(title="Learn pytest")

    assert task.title == "Learn pytest"
    assert task.completed is False
    assert task.id is None
    assert isinstance(task.created_at, datetime)


def test_task_accepts_explicit_values() -> None:
    created_at = datetime(2026, 11, 4, 12, 30)
    task = Task(
        title="Review fixtures",
        completed=True,
        created_at=created_at,
        id=42,
    )

    assert task.title == "Review fixtures"
    assert task.completed is True
    assert task.created_at == created_at
    assert task.id == 42


def test_tasks_receive_independent_default_timestamps() -> None:
    first_task = Task(title="First task")
    second_task = Task(title="Second task")

    assert first_task.created_at is not second_task.created_at
