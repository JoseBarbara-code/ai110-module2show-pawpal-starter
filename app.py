import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

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

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    name = pet_name.strip()
    if not name:
        st.warning("Please enter a pet name.")
    elif any(pet.name == name for pet in owner.pets):
        st.warning(f"You already have a pet named {name}.")
    else:
        owner.add_pet(Pet(name, species))
        st.success(f"Added {name} the {species}.")

if owner.pets:
    st.write("Your pets:")
    st.table(
        [{"name": pet.name, "species": pet.species, "tasks": len(pet.tasks)} for pet in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Pick a pet, then add its care tasks.")

# The dropdown holds pet names, not Pet objects. Streamlit hands back a copy of
# whatever a widget holds, so a task added to a copied Pet would be lost.
selected_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    title = task_title.strip()
    if selected_pet_name is None:
        st.warning("Add a pet first, then you can give it tasks.")
    elif not title:
        st.warning("Please enter a task title.")
    else:
        # Find the real Pet stored on the owner and add the task to it.
        for pet in owner.pets:
            if pet.name == selected_pet_name:
                pet.add_task(Task(title, int(duration), priority))
                st.success(f"Added {title} for {pet.name}.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": task.pet_name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
            }
            for task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Picks tasks from highest to lowest priority until the available time runs out.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    if not all_tasks:
        st.info("Add some tasks first.")
    else:
        if plan:
            st.write("Today's schedule:")
            st.table(
                [
                    {
                        "task": task.title,
                        "pet": task.pet_name,
                        "minutes": task.duration_minutes,
                        "priority": task.priority,
                    }
                    for task in plan
                ]
            )
        else:
            st.warning("No tasks fit in the time available.")

        used = sum(task.duration_minutes for task in plan)
        st.write(
            f"Time used: {used} of {owner.available_minutes} min "
            f"({owner.available_minutes - used} min left)"
        )

        if scheduler.skipped_tasks:
            skipped_lines = "\n".join(f"- {task.describe()}" for task in scheduler.skipped_tasks)
            st.warning("Skipped (not enough time left):\n\n" + skipped_lines)

        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan(plan))
