"""PawPal+ demo — build an owner with pets and tasks, then print today's schedule."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # Create an owner.
    owner = Owner("Khoa")

    # Create at least two pets.
    rex = Pet("Rex", "dog")
    milo = Pet("Milo", "cat")

    # Add at least three tasks with different times.
    rex.add_task(Task("Morning walk", "08:00", "daily"))
    rex.add_task(Task("Evening walk", "18:00", "daily"))
    milo.add_task(Task("Feed breakfast", "07:30", "daily"))
    milo.add_task(Task("Clean litter box", "19:00", "daily"))

    # Register the pets under the owner.
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Build and print Today's Schedule, time-ordered across all pets.
    scheduler = Scheduler(owner)
    schedule = scheduler.build_schedule(pending_only=True)

    print("Today's Schedule")
    print("=" * 40)
    for pet, task in schedule:
        print(f"{task.time}  {pet.name} ({pet.species}): {task.description}")


if __name__ == "__main__":
    main()
