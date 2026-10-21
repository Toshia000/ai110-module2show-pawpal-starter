from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Priority(IntEnum):
    """Task priority; lower value means more important, so sorting by priority puts HIGH first."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


# eq=False: entities compare and hash by identity, so two identical-looking tasks stay distinct.
# Back-references and child lists are init=False and filled via add_pet/add_task to stay in sync.
@dataclass(eq=False)
class Task:
    name: str
    duration: int  # minutes
    priority: Priority
    pet: Pet | None = field(default=None, init=False, repr=False)  # set by Pet.add_task


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
        self.owner = owner

    def sort_by_priority(self) -> list[Task]:
        """Return the owner's tasks ordered from most to least important."""
        pass

    def generate_daily_schedule(self) -> list[Task]:
        """Build the day's ordered task list."""
        pass
