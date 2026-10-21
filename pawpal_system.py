from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    """Task priority; lower value means more important, so sorting by value puts HIGH first."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: Priority
    pet: Pet | None = field(default=None, repr=False, compare=False)


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner | None = field(default=None, repr=False, compare=False)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet."""
        pass


@dataclass
class Owner:
    first_name: str
    last_name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass


class Scheduler:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to be scheduled."""
        pass

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered from most to least important."""
        pass

    def generate_daily_schedule(self) -> list[Task]:
        """Build the day's ordered task list."""
        pass
