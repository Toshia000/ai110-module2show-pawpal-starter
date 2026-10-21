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


# How far ahead the next occurrence lands; ONCE is absent because it never recurs.
RECURRENCE_INTERVALS = {
    Frequency.DAILY: datetime.timedelta(days=1),
    Frequency.WEEKLY: datetime.timedelta(weeks=1),
}


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
    due_date: datetime.date | None = None  # None means due today (or whenever it is checked)
    pet: Pet | None = field(default=None, init=False, repr=False)  # set by Pet.add_task

    def mark_complete(self) -> Task | None:
        """Mark this task as done; for a daily or weekly task, also create the next occurrence.

        The next occurrence is a fresh, pending copy due one day (daily) or seven days (weekly)
        after this task's due date, added to the same pet. Returns it, or None when no
        occurrence was created: a one-off task, or a task that was already complete, so that
        completing twice cannot spawn duplicates.
        """
        if self.completed:
            return None
        self.completed = True

        interval = RECURRENCE_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        next_task = Task(
            self.name,
            self.duration,
            self.priority,
            self.frequency,
            time=self.time,
            due_date=(self.due_date or datetime.date.today()) + interval,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task


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

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return the owner's tasks matching every given filter; None skips that filter.

        pet_name is matched case-insensitively against the pet's full name.
        """
        wanted_pet = pet_name.strip().casefold() if pet_name is not None else None
        return [
            task
            for task in self.owner.get_all_tasks()
            if (completed is None or task.completed == completed)
            and (wanted_pet is None or (task.pet and task.pet.name.casefold() == wanted_pet))
        ]

    def generate_daily_schedule(self, today: datetime.date | None = None) -> list[Task]:
        """Build the day's ordered task list: pending tasks due by today, most important first.

        Tasks due on a later date, such as tomorrow's copy of a daily task, are left out.
        """
        today = today or datetime.date.today()
        return [
            task
            for task in self.sort_by_priority()
            if not task.completed and (task.due_date is None or task.due_date <= today)
        ]
