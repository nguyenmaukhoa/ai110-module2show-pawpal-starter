"""PawPal+ — pet care planning assistant.

Skeleton generated from diagrams/uml.mmd.
Four core components: Owner, Pet, Task, Scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single care activity for a pet."""

    title: str
    duration_minutes: int
    priority: str

    def priority_weight(self) -> int:
        """Return a numeric weight for this task's priority."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by an Owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return the pet's tasks."""
        raise NotImplementedError


class Owner:
    """A person who owns one or more pets."""

    def __init__(self, name: str, preferences: dict | None = None) -> None:
        self.name: str = name
        self.pets: list[Pet] = []
        self.preferences: dict = preferences if preferences is not None else {}

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def list_pets(self) -> list[Pet]:
        """Return the owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily care schedule from a set of tasks."""

    def __init__(self, day_minutes: int) -> None:
        self.tasks: list[Task] = []
        self.day_minutes: int = day_minutes

    def build_schedule(self, tasks: list[Task]) -> list[Task]:
        """Return an ordered list of tasks that fit within the day."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of the schedule."""
        raise NotImplementedError
