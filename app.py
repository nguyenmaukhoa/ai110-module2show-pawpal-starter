import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def tasks_to_rows(pairs: list[tuple[Pet, Task]]) -> list[dict]:
    """Turn (pet, task) pairs into ordered rows for st.table display."""
    return [
        {
            "Time": task.time,
            "Pet": pet.name,
            "Species": pet.species,
            "Task": task.description,
            "Frequency": task.frequency,
            "Status": "✓ Done" if task.completed else "○ Pending",
        }
        for pet, task in pairs
    ]

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Create the Owner + Scheduler once and reuse them across Streamlit reruns.
owner_name = st.text_input("Owner name", value="Jordan")
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.subheader("Add a Pet")
col_a, col_b = st.columns(2)
with col_a:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_b:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if owner.get_pet(pet_name) is not None:
        st.warning(f"{pet_name} is already registered.")
    else:
        owner.add_pet(Pet(pet_name, species))
        st.success(f"Added {pet_name} ({species}).")

pets = owner.list_pets()
if pets:
    st.write("Current pets:")
    for pet in pets:
        st.markdown(f"- {pet}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if not pets:
    st.info("Add a pet first, then you can assign tasks to it.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        target_pet = st.selectbox("Pet", [pet.name for pet in pets])
    with col2:
        task_description = st.text_input("Description", value="Morning walk")
    with col3:
        task_time = st.text_input("Time (HH:MM)", value="08:00")

    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

    if st.button("Add task"):
        pet = owner.get_pet(target_pet)
        pet.add_task(Task(task_description, task_time, frequency))
        st.success(f"Added '{task_description}' at {task_time} for {pet.name}.")

st.divider()

st.subheader("Build Schedule")
st.caption("Orders every pending task across all pets by time of day.")

if st.button("Generate schedule"):
    schedule = scheduler.build_schedule(pending_only=True)
    if not schedule:
        st.info("No pending tasks to schedule.")
    else:
        st.success(f"Planned {len(schedule)} task(s), ordered by time of day.")
        st.table(tasks_to_rows(schedule))

st.divider()

st.subheader("Today's Tasks")
st.caption("Mark a task done — recurring tasks auto-schedule their next occurrence.")

# Show (and clear) any confirmation left over from the previous rerun.
if flash := st.session_state.pop("task_flash", None):
    st.success(flash)

# Warn about pending tasks that collide at the same time of day.
conflicts = scheduler.find_conflicts(pending_only=True)
if conflicts:
    slots = ", ".join(time for time, _ in conflicts)
    st.warning(f"⚠️ Scheduling conflict at {slots} — tasks overlap.")
    for time, pairs in conflicts:
        names = ", ".join(f"{pet.name}: {task.description}" for pet, task in pairs)
        st.markdown(f"- **{time}** — {names}")

pending = scheduler.filter_tasks(completed=False)
if not pending:
    st.info("No pending tasks. All caught up! 🎉")
else:
    pending.sort(key=lambda pair: pair[1].time)
    for pet, task in pending:
        task_col, btn_col = st.columns([4, 1])
        with task_col:
            st.markdown(f"{task.time}  **{pet.name}**: {task.description} ({task.frequency})")
        with btn_col:
            # Key must be unique and stable per task across reruns.
            if st.button("Done", key=f"done-{pet.name}-{id(task)}"):
                following = scheduler.complete_task(task)
                if following is not None:
                    st.session_state.task_flash = (
                        f"Completed! Next '{task.description}' scheduled for "
                        f"{following.due_date}."
                    )
                else:
                    st.session_state.task_flash = f"Completed '{task.description}'."
                st.rerun()

st.divider()

st.subheader("Filter Tasks")
st.caption("Browse tasks by pet and/or completion status.")

if not pets:
    st.info("Add a pet and some tasks first.")
else:
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_choice = st.selectbox("Pet", ["All pets"] + [pet.name for pet in pets])
    with fcol2:
        status_choice = st.selectbox("Status", ["All", "Pending", "Done"])

    pet_filter = None if pet_choice == "All pets" else pet_choice
    completed_filter = {"All": None, "Pending": False, "Done": True}[status_choice]

    results = scheduler.filter_tasks(pet_name=pet_filter, completed=completed_filter)
    if not results:
        st.info("No tasks match those filters.")
    else:
        # Order the matches chronologically before displaying them.
        results.sort(key=lambda pair: pair[1].time)
        st.success(f"Showing {len(results)} matching task(s).")
        st.table(tasks_to_rows(results))
