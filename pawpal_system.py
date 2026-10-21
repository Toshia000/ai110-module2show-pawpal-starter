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

        The next due date is the old due date plus the interval from RECURRENCE_INTERVALS
        (today stands in when due_date is None), so a task finished late keeps its cadence and
        the copy can already be overdue. The copy is not marked complete, and a task not
        attached to a pet yields an unattached copy. O(1) apart from the list scan in
        Pet.add_task.
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


def _describe(task: Task) -> str:
    """Return e.g. "Mochi's Walk (09:00-09:30)" for a timed task that belongs to a pet.

    The end time is start plus duration, so a task running past midnight shows the wrapped
    clock time (23:30 + 90 min reads "23:30-01:00"). Requires task.time and task.pet to be set.
    """
    start = datetime.datetime.combine(datetime.date.min, task.time)
    end = start + datetime.timedelta(minutes=task.duration)
    return f"{task.pet.name}'s {task.name} ({start:%H:%M}-{end:%H:%M})"


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans tasks for the given owner."""
        self.owner = owner

    def sort_by_priority(self) -> list[Task]:
        """Return the owner's tasks ordered from most to least important."""
        return sorted(self.owner.get_all_tasks(), key=lambda task: task.priority)

    def sort_by_time(self) -> list[Task]:
        """Return the owner's tasks ordered earliest first; tasks without a time go last.

        Sorts on the key (has no time, time of day, priority): the leading flag pushes untimed
        tasks to the end, where they are ordered among themselves by priority. Ties are then
        broken by insertion order (sorted is stable). Only the time of day is compared, not
        due_date, so a task due tomorrow at 08:00 still sorts before one due today at 09:00.
        Completed tasks are included. Runs in O(n log n) and returns a new list.
        """
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda task: (task.time is None, task.time or datetime.time.min, task.priority),
        )

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return the owner's tasks matching every given filter; None skips that filter.

        completed=True keeps only finished tasks and completed=False only pending ones. pet_name
        is matched case-insensitively and ignoring surrounding spaces against the pet's full
        name, never as a substring, so an unknown name returns []. The filters combine with AND,
        and with neither given every task is returned. One O(n) pass that keeps the owner's
        pet-then-insertion order.
        """
        wanted_pet = pet_name.strip().casefold() if pet_name is not None else None
        return [
            task
            for task in self.owner.get_all_tasks()
            if (completed is None or task.completed == completed)
            and (wanted_pet is None or (task.pet and task.pet.name.casefold() == wanted_pet))
        ]

    def find_conflicts(self, today: datetime.date | None = None) -> list[tuple[Task, Task]]:
        """Return pairs of pending timed tasks whose time ranges overlap, for any pets.

        A task occupies [start, start + duration) on its due date (today if it has none), so
        back-to-back tasks do not conflict and tasks on different days never do. Completed and
        untimed tasks are ignored. Each pair is ordered earliest first, ties by priority.

        Sweep-line approach: build each task's (start, end) as full datetimes, sort by start,
        then compare each task only with the tasks that start before it ends. Because the list
        is sorted, the inner loop stops at the first task starting at or after that end, so
        nothing later can overlap either. A long task is compared with every task it covers,
        not just its neighbour. Using datetimes also handles tasks that run past midnight.
        Costs O(n log n) for the sort plus O(n + k) for the sweep, where k is the number of
        overlapping pairs returned (k can approach n squared when everything overlaps).

        Args:
            today: the date used for tasks with no due_date; defaults to date.today().
        """
        today = today or datetime.date.today()
        occupied = sorted(
            (
                (start, start + datetime.timedelta(minutes=task.duration), task)
                for task in self.owner.get_all_tasks()
                if task.time and not task.completed
                for start in [datetime.datetime.combine(task.due_date or today, task.time)]
            ),
            key=lambda slot: (slot[0], slot[2].priority),
        )
        conflicts = []
        for i, (_, first_end, first) in enumerate(occupied):
            for second_start, _, second in occupied[i + 1 :]:
                if second_start >= first_end:
                    break  # sorted by start, so nothing later can overlap `first` either
                conflicts.append((first, second))
        return conflicts

    def conflict_warnings(self, today: datetime.date | None = None) -> list[str]:
        """Return one human-readable warning per overlapping pair; empty when all is clear.

        Lightweight by design: it only reports. Nothing is raised or blocked, so the caller
        can show the messages and carry on with the schedule as is. It formats the pairs from
        find_conflicts (same detection rules and cost), labelling each one "same pet" or
        "different pets", e.g. "Warning (same pet): Mochi's Walk (09:00-09:30) overlaps
        Mochi's Bath (09:15-09:35)".

        Args:
            today: the date used for tasks with no due_date; defaults to date.today().
        """
        return [
            f"Warning ({'same pet' if first.pet is second.pet else 'different pets'}): "
            f"{_describe(first)} overlaps {_describe(second)}"
            for first, second in self.find_conflicts(today)
        ]

    def generate_daily_schedule(self, today: datetime.date | None = None) -> list[Task]:
        """Build the day's ordered task list: pending tasks due by today, most important first.

        Tasks due on a later date, such as tomorrow's copy of a daily task, are left out.
        Tasks with no due_date count as due today, and overdue ones stay in. Order comes only
        from sort_by_priority, so task.time is not used. Filters the priority-sorted list in
        one pass, so it runs in O(n log n).

        Args:
            today: the cutoff date; defaults to date.today().
        """
        today = today or datetime.date.today()
        return [
            task
            for task in self.sort_by_priority()
            if not task.completed and (task.due_date is None or task.due_date <= today)
        ]
