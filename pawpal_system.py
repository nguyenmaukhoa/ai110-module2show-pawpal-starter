"""PawPal+ — pet care planning assistant.

Four core components:
    Task      — a single care activity (description, time, frequency, done).
    Pet       — pet details plus its list of tasks.
    Owner     — manages multiple pets and exposes all their tasks.
    Scheduler — the "brain": retrieves, organizes, and manages tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single care activity for a pet.

    Attributes:
        description: What needs to be done, e.g. "Morning walk".
        time: Time of day in 24-hour "HH:MM" form, e.g. "08:00".
        frequency: How often it recurs, e.g. "daily", "weekly".
        completed: Whether the task has been done for its current cycle.
    """

    description: str
    time: str
    frequency: str = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to not-done (e.g. at the start of a new cycle)."""
        self.completed = False

    def __str__(self) -> str:
        """Return a compact one-line summary of this task."""
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.time} — {self.description} ({self.frequency})"


@dataclass
class Pet:
    """A pet owned by an Owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]

    def __str__(self) -> str:
        """Return a one-line summary of this pet and its task count."""
        return f"{self.name} ({self.species}) — {len(self.tasks)} task(s)"


class Owner:
    """A person who owns one or more pets and access to all their tasks."""

    def __init__(self, name: str, preferences: dict | None = None) -> None:
        """Create an owner with a name and optional preferences dict."""
        self.name: str = name
        self.pets: list[Pet] = []
        self.preferences: dict = preferences if preferences is not None else {}

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def list_pets(self) -> list[Pet]:
        """Return a copy of this owner's pets."""
        return list(self.pets)

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name (case-insensitive); None if not found."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets, paired with its owning pet."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def __str__(self) -> str:
        """Return a one-line summary of this owner and its pet count."""
        return f"{self.name} — {len(self.pets)} pet(s)"


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans tasks for the given owner."""
        self.owner: Owner = owner

    def all_tasks(self, *, pending_only: bool = False) -> list[tuple[Pet, Task]]:
        """Retrieve every (pet, task) pair, optionally only the pending ones."""
        pairs = self.owner.all_tasks()
        if pending_only:
            pairs = [(pet, task) for pet, task in pairs if not task.completed]
        return pairs

    def build_schedule(self, *, pending_only: bool = True) -> list[tuple[Pet, Task]]:
        """Return tasks ordered by time of day, earliest first (stable on ties)."""
        pairs = self.all_tasks(pending_only=pending_only)
        return sorted(pairs, key=lambda pair: pair[1].time)

    def tasks_by_frequency(self, frequency: str) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs matching the given frequency."""
        return [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if task.frequency.lower() == frequency.lower()
        ]

    def reset_daily(self) -> None:
        """Mark every 'daily' task incomplete to begin a new day's cycle."""
        for _, task in self.owner.all_tasks():
            if task.frequency.lower() == "daily":
                task.mark_incomplete()

    def explain(self) -> str:
        """Return a human-readable, time-ordered agenda of pending tasks."""
        schedule = self.build_schedule(pending_only=True)
        if not schedule:
            return f"{self.owner.name} has no pending tasks. All caught up!"

        lines = [f"Care schedule for {self.owner.name}:"]
        for pet, task in schedule:
            lines.append(f"  {task.time}  {pet.name}: {task.description} ({task.frequency})")
        return "\n".join(lines)


if __name__ == "__main__":
    owner = Owner("Khoa")

    dog = Pet("Rex", "dog")
    dog.add_task(Task("Morning walk", "08:00", "daily"))
    dog.add_task(Task("Vet checkup", "14:30", "monthly"))

    cat = Pet("Milo", "cat")
    cat.add_task(Task("Feed", "07:30", "daily"))
    cat.add_task(Task("Clean litter box", "19:00", "daily"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    print(scheduler.explain())
