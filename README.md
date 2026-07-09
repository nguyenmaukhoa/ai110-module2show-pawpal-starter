# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
========================================
07:30  Milo (cat): Feed breakfast
08:00  Rex (dog): Morning walk
18:00  Rex (dog): Evening walk
19:00  Milo (cat): Clean litter box
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest


# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
============================ test session starts =============================
platform darwin -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/khoanguyen/Documents/AI Engineer/Codepath/Week 3/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 14 items                                                           

test/test_pawpal.py ..............                                     [100%]

============================= 14 passed in 0.01s =============================
```

## 📐 Smarter Scheduling

The `Scheduler` class in [`pawpal_system.py`](pawpal_system.py) is the "brain" of PawPal+. It
is constructed with an `Owner` and reaches across every pet's tasks to sort, filter, detect
conflicts, and manage recurring care.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.build_schedule()` | Orders tasks by time of day, earliest first. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.all_tasks()`, `Scheduler.tasks_by_frequency()` | Filter by pet, completion status, pending-only, or frequency. |
| Conflict detection | `Scheduler.find_conflicts()` | Flags tasks sharing the same start time. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()`, `Scheduler.reset_daily()` | Auto-reschedules daily/weekly tasks. |

### Sorting behavior

- **`Scheduler.sort_by_time(tasks)`** returns a list of tasks ordered by time of day, earliest
  first. It sorts on the `"HH:MM"` string, which compares correctly as long as times are
  zero-padded 24-hour values (e.g. `"08:00"` before `"18:00"`).
- **`Scheduler.build_schedule(pending_only=True)`** produces the actual daily agenda: it gathers
  every `(pet, task)` pair (pending only by default) and returns them sorted by time, so the owner
  sees their day in chronological order. `explain()` renders this schedule as human-readable text.

### Filtering behavior

- **`Scheduler.filter_tasks(pet_name=None, completed=None)`** returns `(pet, task)` pairs filtered
  by pet name (case-insensitive) and/or completion status. Both filters are optional and combine
  with AND; calling it with no arguments returns every task across all pets.
- **`Scheduler.all_tasks(pending_only=False)`** retrieves every `(pet, task)` pair, optionally
  limited to tasks that are not yet completed.
- **`Scheduler.tasks_by_frequency(frequency)`** returns all tasks matching a given frequency
  (e.g. `"daily"`, `"weekly"`).

### Conflict detection logic

- **`Scheduler.find_conflicts(pending_only=False)`** groups every `(pet, task)` pair by its
  `time` and returns only the slots that hold two or more tasks — the clashes an owner needs to
  resolve. It reports conflicts both across pets (walking two dogs at 08:00) and within a single
  pet (feeding and medicating the same cat at 07:30), sorted earliest-first. Detection is by
  **exact start time**; it does not model task duration, so overlapping-but-not-identical times
  are not flagged.

### Recurring task logic

- **`Task.next_occurrence(from_date=None)`** returns a fresh, uncompleted copy of the task with its
  `due_date` advanced by the interval for its frequency (one day for `"daily"`, seven for
  `"weekly"`). It returns `None` for frequencies that do not recur on a fixed interval, so the
  caller can tell there is nothing to reschedule.
- **`Scheduler.complete_task(task)`** marks a task complete and, if it recurs, appends its next
  occurrence to the same pet's task list — so finishing today's walk automatically queues
  tomorrow's.
- **`Scheduler.reset_daily()`** marks every `"daily"` task incomplete to begin a new day's cycle.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
