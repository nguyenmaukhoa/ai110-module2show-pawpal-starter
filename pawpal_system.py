"""PawPal+ — pet care planning assistant.

Four core components:
    Task      — a single care activity (description, time, frequency, done).
    Pet       — pet details plus its list of tasks.
    Owner     — manages multiple pets and exposes all their tasks.
    Scheduler — the "brain": retrieves, organizes, and manages tasks across pets.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

# How many days forward each recurring frequency advances. Frequencies not
# listed here (e.g. "once") do not automatically repeat.
_RECUR_DAYS: dict[str, int] = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single care activity for a pet.

    Attributes:
        description: What needs to be done, e.g. "Morning walk".
        time: Time of day in 24-hour "HH:MM" form, e.g. "08:00".
        frequency: How often it recurs, e.g. "daily", "weekly".
        completed: Whether the task has been done for its current cycle.
        due_date: The calendar day this task is scheduled for (defaults to today).
    """

    description: str
    time: str
    frequency: str = "daily"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self, *, from_date: date | None = None) -> Task | None:
        """Return a fresh, uncompleted Task for this task's next occurrence.

        The new task's ``due_date`` is advanced from ``from_date`` (default:
        today) by the interval for its frequency — one day for "daily", seven
        for "weekly". Returns ``None`` for frequencies that do not recur on a
        fixed interval, so the caller can tell there is nothing to reschedule.
        """
        step = _RECUR_DAYS.get(self.frequency.lower())
        if step is None:
            return None
        base = from_date if from_date is not None else date.today()
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            due_date=base + timedelta(days=step),
        )

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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks ordered by time of day, earliest first.

        Sorts on the "HH:MM" string, which compares correctly as long as the
        times are zero-padded 24-hour values (e.g. "08:00" before "18:00").
        """
        return sorted(tasks, key=lambda task: task.time)

    def build_schedule(self, *, pending_only: bool = True) -> list[tuple[Pet, Task]]:
        """Return tasks ordered by time of day, earliest first (stable on ties)."""
        pairs = self.all_tasks(pending_only=pending_only)
        return sorted(pairs, key=lambda pair: pair[1].time)

    def complete_task(self, task: Task, *, from_date: date | None = None) -> Task | None:
        """Mark ``task`` complete and auto-schedule its next occurrence.

        For a recurring task (daily/weekly), a fresh, uncompleted copy is
        created with its due date advanced and appended to the same pet's task
        list. Returns the newly created follow-up task, or ``None`` if the task
        does not recur (or its owning pet cannot be found).
        """
        task.mark_complete()
        following = task.next_occurrence(from_date=from_date)
        if following is None:
            return None
        for pet in self.owner.pets:
            if task in pet.tasks:
                pet.add_task(following)
                return following
        return None

    def filter_tasks(
        self,
        *,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs filtered by pet name and/or completion status.

        Both filters are optional and combine with AND:
            - pet_name: keep only tasks belonging to this pet (case-insensitive).
            - completed: keep only tasks whose ``completed`` matches this value
              (True for done, False for pending).

        With no arguments, returns every task across all pets.
        """
        pairs = self.owner.all_tasks()
        if pet_name is not None:
            pairs = [
                (pet, task)
                for pet, task in pairs
                if pet.name.lower() == pet_name.lower()
            ]
        if completed is not None:
            pairs = [(pet, task) for pet, task in pairs if task.completed == completed]
        return pairs

    def find_conflicts(
        self, *, pending_only: bool = False
    ) -> list[tuple[str, list[tuple[Pet, Task]]]]:
        """Detect tasks scheduled at the same time of day.

        Groups every (pet, task) pair by its ``time`` and returns only the time
        slots that hold two or more tasks — these are the clashes an owner
        needs to resolve. Conflicts across different pets and within a single
        pet are both reported (e.g. walking two dogs at 08:00, or feeding and
        medicating the same cat at 07:30).

        Args:
            pending_only: If True, ignore already-completed tasks.

        Returns:
            A list of ``(time, pairs)`` tuples sorted earliest-first, where
            ``pairs`` is the list of clashing (pet, task) pairs at that time.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = defaultdict(list)
        for pet, task in self.all_tasks(pending_only=pending_only):
            by_time[task.time].append((pet, task))

        conflicts = [
            (time, pairs) for time, pairs in by_time.items() if len(pairs) > 1
        ]
        return sorted(conflicts, key=lambda item: item[0])

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
