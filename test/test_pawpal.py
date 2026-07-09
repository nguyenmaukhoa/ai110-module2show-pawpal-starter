"""Simple tests for the PawPal+ system."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Scheduler, Task


def _owner_with_tasks() -> Owner:
    """Build an owner with two pets and a mix of pending/done tasks."""
    owner = Owner("Khoa")

    rex = Pet("Rex", "dog")
    rex.add_task(Task("Evening walk", "18:00", "daily"))
    morning = Task("Morning walk", "08:00", "daily")
    morning.mark_complete()
    rex.add_task(morning)

    milo = Pet("Milo", "cat")
    milo.add_task(Task("Feed breakfast", "07:30", "daily"))

    owner.add_pet(rex)
    owner.add_pet(milo)
    return owner


def test_sort_by_time_orders_earliest_first():
    """sort_by_time() should order tasks chronologically by their HH:MM time."""
    scheduler = Scheduler(Owner("Khoa"))
    tasks = [
        Task("Evening walk", "18:00"),
        Task("Feed", "07:30"),
        Task("Lunch", "12:00"),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [task.time for task in ordered] == ["07:30", "12:00", "18:00"]


def test_filter_tasks_by_pet_name_is_case_insensitive():
    """filter_tasks(pet_name=...) should return only that pet's tasks."""
    scheduler = Scheduler(_owner_with_tasks())

    pairs = scheduler.filter_tasks(pet_name="rex")

    assert len(pairs) == 2
    assert all(pet.name == "Rex" for pet, _ in pairs)


def test_filter_tasks_by_completion_status():
    """filter_tasks(completed=...) should split done from pending tasks."""
    scheduler = Scheduler(_owner_with_tasks())

    pending = scheduler.filter_tasks(completed=False)
    done = scheduler.filter_tasks(completed=True)

    assert {task.description for _, task in pending} == {"Evening walk", "Feed breakfast"}
    assert {task.description for _, task in done} == {"Morning walk"}


def test_filter_tasks_combines_pet_and_status():
    """Both filters should combine with AND."""
    scheduler = Scheduler(_owner_with_tasks())

    pairs = scheduler.filter_tasks(pet_name="Rex", completed=False)

    assert len(pairs) == 1
    assert pairs[0][1].description == "Evening walk"


def test_next_occurrence_advances_daily_by_one_day():
    """A daily task's next occurrence is due one day later and not completed."""
    from datetime import date

    task = Task("Morning walk", "08:00", "daily")

    # Advance from a fixed date so the test is independent of the real "today".
    following = task.next_occurrence(from_date=date(2026, 7, 7))

    assert following is not None
    assert following.due_date == date(2026, 7, 8)
    assert following.completed is False
    assert following.description == "Morning walk"


def test_next_occurrence_advances_weekly_by_seven_days():
    """A weekly task's next occurrence is due seven days later."""
    from datetime import date

    task = Task("Bath", "10:00", "weekly")

    following = task.next_occurrence(from_date=date(2026, 7, 7))

    assert following.due_date == date(2026, 7, 14)


def test_next_occurrence_none_for_non_recurring():
    """A non-recurring frequency should not produce a follow-up task."""
    task = Task("Vet checkup", "14:30", "monthly")

    assert task.next_occurrence() is None


def test_complete_task_appends_next_occurrence_to_same_pet():
    """Completing a recurring task auto-adds its next occurrence to the pet."""
    from datetime import date

    owner = Owner("Khoa")
    rex = Pet("Rex", "dog")
    walk = Task("Morning walk", "08:00", "daily")
    rex.add_task(walk)
    owner.add_pet(rex)
    scheduler = Scheduler(owner)

    following = scheduler.complete_task(walk, from_date=date(2026, 7, 7))

    assert walk.completed is True
    assert following in rex.tasks
    assert following.due_date == date(2026, 7, 8)
    assert len(rex.tasks) == 2


def test_find_conflicts_detects_same_time_across_pets():
    """Two pets scheduled at the same time should be reported as a conflict."""
    owner = Owner("Khoa")
    rex = Pet("Rex", "dog")
    rex.add_task(Task("Walk", "08:00", "daily"))
    milo = Pet("Milo", "cat")
    milo.add_task(Task("Feed", "08:00", "daily"))
    owner.add_pet(rex)
    owner.add_pet(milo)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    time, pairs = conflicts[0]
    assert time == "08:00"
    assert len(pairs) == 2


def test_find_conflicts_detects_same_time_within_one_pet():
    """Two tasks for the same pet at one time should also conflict."""
    owner = Owner("Khoa")
    rex = Pet("Rex", "dog")
    rex.add_task(Task("Feed", "07:30", "daily"))
    rex.add_task(Task("Medicate", "07:30", "daily"))
    owner.add_pet(rex)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert conflicts[0][0] == "07:30"
    assert len(conflicts[0][1]) == 2


def test_find_conflicts_returns_empty_when_times_differ():
    """Distinct times should produce no conflicts."""
    owner = Owner("Khoa")
    rex = Pet("Rex", "dog")
    rex.add_task(Task("Morning walk", "08:00", "daily"))
    rex.add_task(Task("Evening walk", "18:00", "daily"))
    owner.add_pet(rex)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts() == []


def test_find_conflicts_pending_only_ignores_completed():
    """pending_only should exclude completed tasks from conflict detection."""
    owner = Owner("Khoa")
    rex = Pet("Rex", "dog")
    done = Task("Walk", "08:00", "daily")
    done.mark_complete()
    rex.add_task(done)
    rex.add_task(Task("Feed", "08:00", "daily"))
    owner.add_pet(rex)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts(pending_only=True) == []  # one pending task at 08:00
    assert len(scheduler.find_conflicts(pending_only=False)) == 1


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() should set the task to completed."""
    task = Task("Morning walk", "08:00", "daily")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task should increase the pet's task count."""
    pet = Pet("Rex", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed", "07:30", "daily"))

    assert len(pet.tasks) == 1
