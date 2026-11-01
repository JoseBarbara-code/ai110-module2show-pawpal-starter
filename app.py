from datetime import date, datetime

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

PRIORITIES = ["low", "medium", "high"]
FREQUENCIES = ["daily", "weekly", "once"]


def find_pet(owner: Owner, name: str | None) -> Pet | None:
    """Return the real Pet object with this name from the owner (or None)."""
    for pet in owner.pets:
        if pet.name == name:
            return pet
    return None


def task_label(task: Task) -> str:
    """Return a short label for dropdowns, like 'Breakfast (Mochi), due 2026-11-01 at 07:00'."""
    label = f"{task.title} ({task.pet_name}), due {task.due_date}"
    if task.time:
        label += f" at {task.time}"
    return label


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+! Add your pets and their care tasks, then generate a daily
schedule that fits the time you have available.
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

st.subheader("Owner and Pets")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Minutes available today", min_value=0, max_value=1440, value=60
)

# Create the Owner only once. Streamlit reruns this whole file on every click,
# so keeping the Owner in session_state stops pets and tasks from being lost.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, int(available_minutes))
owner = st.session_state.owner

# Keep the owner's info in sync with the inputs (this doesn't touch pets or tasks).
owner.name = owner_name
owner.available_minutes = int(available_minutes)

# The Scheduler doesn't store anything between clicks, so it's fine to make a new one each run.
scheduler = Scheduler(owner)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    name = pet_name.strip()
    if not name:
        st.warning("Please enter a pet name.")
    elif find_pet(owner, name) is not None:
        st.warning(f"You already have a pet named {name}.")
    else:
        owner.add_pet(Pet(name, species))
        st.success(f"Added {name} the {species}.")

if owner.pets:
    st.write("Your pets:")
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "tasks to do": len([task for task in pet.tasks if not task.completed]),
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Pick a pet, then add its care tasks. Leave the time empty for tasks that can happen anytime.")

# The dropdown holds pet names, not Pet objects. Streamlit hands back a copy of
# whatever a widget holds, so a task added to a copied Pet would be lost.
selected_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", PRIORITIES, index=2)

col4, col5, col6 = st.columns(3)
with col4:
    task_time = st.time_input("Time (optional)", value=None, step=300)
with col5:
    frequency = st.selectbox("Repeats", FREQUENCIES)
with col6:
    due_date = st.date_input("Due date", value=date.today())

if st.button("Add task"):
    title = task_title.strip()
    pet = find_pet(owner, selected_pet_name)
    if pet is None:
        st.warning("Add a pet first, then you can give it tasks.")
    elif not title:
        st.warning("Please enter a task title.")
    else:
        # st.time_input gives a time object (or None), but Task expects "HH:MM" text.
        time_text = task_time.strftime("%H:%M") if task_time is not None else ""
        try:
            task = Task(title, int(duration), priority, frequency=frequency,
                        time=time_text, due_date=due_date)
        except ValueError as error:
            st.error(f"Couldn't add that task: {error}")
        else:
            pet.add_task(task)
            when = f"at {task.time}" if task.time else "anytime"
            # Save the message and refresh the page so every table above shows the new task.
            st.session_state.task_message = (
                f"Added {title} for {pet.name} ({when} on {task.due_date}, repeats: {frequency})."
            )
            st.rerun()

if "task_message" in st.session_state:
    st.success(st.session_state.pop("task_message"))

st.markdown("#### Mark a task complete")
open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
if open_tasks:
    # The dropdown holds list positions (0, 1, 2, ...) instead of Task objects, because
    # Streamlit hands back copies of widget values. The position finds the real task.
    choice = st.selectbox(
        "Task to complete",
        range(len(open_tasks)),
        format_func=lambda i: task_label(open_tasks[i]),
    )
    if st.button("Mark complete"):
        task = open_tasks[choice]
        pet = find_pet(owner, task.pet_name)
        # complete_task marks it done and adds the next copy for daily/weekly tasks.
        next_task = pet.complete_task(task)
        if next_task is None:
            message = f"Completed {task.title} for {pet.name}. It doesn't repeat."
        else:
            message = f"Completed {task.title} for {pet.name}. The next one is due {next_task.due_date}."
        # Refresh so the finished task leaves this dropdown and can't be picked again.
        st.session_state.complete_message = message
        st.rerun()
else:
    st.info("No unfinished tasks to complete.")

if "complete_message" in st.session_state:
    st.success(st.session_state.pop("complete_message"))

st.markdown("#### Edit a task")
# Use the pets' own task order here: editing never changes it, so the same task
# stays selected after you save.
edit_tasks = owner.get_all_tasks()
if edit_tasks:
    # Like "Mark complete", the dropdown holds list positions, not Task objects.
    # The number at the front keeps tasks with the same title apart. The fixed key
    # keeps the same task selected after a save changes its label.
    edit_choice = st.selectbox(
        "Task to edit",
        range(len(edit_tasks)),
        format_func=lambda i: (
            f"{i + 1}. {task_label(edit_tasks[i])}" + (" [done]" if edit_tasks[i].completed else "")
        ),
        key="task_to_edit",
    )
    task_to_edit = edit_tasks[edit_choice]

    # Each task gets its own set of inputs (keyed by the task's id), so they start
    # with that task's current values whenever you pick a different task.
    key = f"edit_{id(task_to_edit)}"
    current_time = (
        datetime.strptime(task_to_edit.time, "%H:%M").time() if task_to_edit.time else None
    )
    with st.form(key):
        edit_col1, edit_col2, edit_col3 = st.columns(3)
        with edit_col1:
            new_title = st.text_input("Title", value=task_to_edit.title, key=f"{key}_title")
        with edit_col2:
            new_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240,
                value=task_to_edit.duration_minutes, key=f"{key}_duration",
            )
        with edit_col3:
            new_priority = st.selectbox(
                "Priority", PRIORITIES, index=PRIORITIES.index(task_to_edit.priority),
                key=f"{key}_priority",
            )
        edit_col4, edit_col5, edit_col6 = st.columns(3)
        with edit_col4:
            new_time = st.time_input("Time (optional)", value=current_time, step=300, key=f"{key}_time")
        with edit_col5:
            new_frequency = st.selectbox(
                "Repeats", FREQUENCIES, index=FREQUENCIES.index(task_to_edit.frequency),
                key=f"{key}_frequency",
            )
        with edit_col6:
            new_due_date = st.date_input("Due date", value=task_to_edit.due_date, key=f"{key}_due")
        save_clicked = st.form_submit_button("Save changes")

    if save_clicked:
        title = new_title.strip()
        if not title:
            st.warning("Please enter a task title.")
        else:
            time_text = new_time.strftime("%H:%M") if new_time is not None else ""
            try:
                # edit() checks the new values first and changes the real task only if they're valid.
                task_to_edit.edit(title, int(new_duration), new_priority, time_text,
                                  new_due_date, new_frequency)
            except ValueError as error:
                st.error(f"Couldn't save those changes: {error}")
            else:
                st.session_state.edit_message = f"Saved changes to {title} for {task_to_edit.pet_name}."
                st.rerun()
else:
    st.info("No tasks to edit yet.")

if "edit_message" in st.session_state:
    st.success(st.session_state.pop("edit_message"))

st.markdown("#### Task list")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    pet_filter = st.selectbox("Show tasks for", ["All pets"] + [pet.name for pet in owner.pets])
with filter_col2:
    status_filter = st.selectbox("Status", ["All", "Not done", "Done"])

# Turn the dropdown choices into filter_tasks() arguments (None means "don't filter on this").
pet_name_arg = None if pet_filter == "All pets" else pet_filter
completed_arg = {"All": None, "Not done": False, "Done": True}[status_filter]
shown_tasks = scheduler.sort_by_time(
    scheduler.filter_tasks(pet_name=pet_name_arg, completed=completed_arg)
)

if not owner.get_all_tasks():
    st.info("No tasks yet. Add one above.")
elif not shown_tasks:
    st.info("No tasks match these filters.")
else:
    st.table(
        [
            {
                "due": str(task.due_date),
                "time": task.time or "anytime",
                "pet": task.pet_name,
                "title": task.title,
                "minutes": task.duration_minutes,
                "priority": task.priority,
                "repeats": task.frequency,
                "status": "done" if task.completed else "to do",
            }
            for task in shown_tasks
        ]
    )

# Warn about unfinished tasks booked at the same date and start time (any pets).
for warning in scheduler.find_conflicts():
    st.warning(warning)

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Tasks due today (or overdue) are picked from highest to lowest priority until the "
    "available time runs out, then listed by time of day."
)

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()

    if not plan and not scheduler.skipped_tasks:
        st.info("Nothing to schedule today. Add tasks that are due today and not done yet.")
    else:
        used = sum(task.duration_minutes for task in plan)
        if plan:
            st.success(
                f"Planned {len(plan)} task(s): {used} of {owner.available_minutes} min used "
                f"({owner.available_minutes - used} min left)."
            )
            st.table(
                [
                    {
                        "time": task.time or "anytime",
                        "task": task.title,
                        "pet": task.pet_name,
                        "minutes": task.duration_minutes,
                        "priority": task.priority,
                        "due": str(task.due_date),
                    }
                    for task in scheduler.sort_by_time(plan)
                ]
            )
        else:
            st.warning("No tasks fit in the time available.")

        for warning in scheduler.find_conflicts(plan):
            st.warning(f"In today's plan: {warning}")

        if scheduler.skipped_tasks:
            skipped_lines = "\n".join(f"- {task.describe()}" for task in scheduler.skipped_tasks)
            st.warning("Skipped (not enough time left):\n\n" + skipped_lines)

        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan(plan))
