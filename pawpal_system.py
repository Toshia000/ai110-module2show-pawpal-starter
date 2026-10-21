from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum, IntEnum


class Priority(IntEnum):
    """Task priority; lower value means more important, so sorting by priority puts HIGH first."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


class Frequency(Enum):
    """How often a task recurs."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# eq=False: entities compare and hash by identity, so two identical-looking tasks stay distinct.
# Back-references and child lists are init=False and filled via add_pet/add_task to stay in sync.
@dataclass(eq=False)
class Task:
    name: str
    duration: int  # minutes
    priority: Priority
    frequency: Frequency = Frequency.DAILY
    completed: bool = False
    time: datetime.time | None = None  # scheduled time of day; None means unscheduled
    pet: Pet | None = field(default=None, init=False, repr=False)  # set by Pet.add_task

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass(eq=False)
class Pet:
    name: str
    species: str
    owner: Owner | None = field(default=None, init=False, repr=False)  # set by Owner.add_pet
    tasks: list[Task] = field(default_factory=list, init=False)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet and set task.pet."""
        if task.pet is not None and task.pet is not self:
            raise ValueError(f"Task '{task.name}' is already assigned to another pet")
        if task not in self.tasks:
            self.tasks.append(task)
        task.pet = self


@dataclass(eq=False)
class Owner:
    first_name: str
    last_name: str
    pets: list[Pet] = field(default_factory=list, init=False)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and set pet.owner."""
        if pet.owner is not None and pet.owner is not self:
            raise ValueError(f"Pet '{pet.name}' already belongs to another owner")
        if pet not in self.pets:
            self.pets.append(pet)
        pet.owner = self

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans tasks for the given owner."""
        self.owner = owner

    def sort_by_priority(self) -> list[Task]:
        """Return the owner's tasks ordered from most to least important."""
        return sorted(self.owner.get_all_tasks(), key=lambda task: task.priority)

    def sort_by_time(self) -> list[Task]:
        """Return the owner's tasks ordered earliest first; tasks without a time go last.

        Ties are broken by priority, then by insertion order (sorted is stable).
        """
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda task: (task.time is None, task.time or datetime.time.min, task.priority),
        )

    def generate_daily_schedule(self) -> list[Task]:
        """Build the day's ordered task list: pending tasks, most important first."""
        return [task for task in self.sort_by_priority() if not task.completed]
