from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    title: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None