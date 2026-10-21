from datetime import date, datetime, time, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

DAY_START = time(8, 0)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

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

st.subheader("Owner and Pets")
col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First name", value="Jordan")
with col2:
    last_name = st.text_input("Last name", value="Lee")

# Streamlit reruns this script on every interaction, so keep the Owner in the session.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(first_name, last_name)
owner = st.session_state.owner
owner.first_name, owner.last_name = first_name, last_name

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species))
    else:
        st.warning("Enter a pet name first.")

if owner.pets:
    st.write("Current pets:")
    st.table([{"Name": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Pick a pet and add tasks for it. The scheduler uses the tasks of all pets.")

if owner.pets:
    # Select by index: st.selectbox returns a copy of object options, not the Pet itself.
    pet_index = st.selectbox(
        "Pet", list(range(len(owner.pets))), format_func=lambda i: owner.pets[i].name
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox(
            "Priority", list(Priority), format_func=lambda level: level.name.capitalize()
        )

    if st.button("Add task"):
        if task_title.strip():
            owner.pets[pet_index].add_task(Task(task_title.strip(), int(duration), priority))
        else:
            st.warning("Enter a task title first.")
else:
    st.info("Add a pet before adding tasks.")

if owner.get_all_tasks():
    st.write("Current tasks:")
    st.table(
        [
            {
                "Pet": pet.name,
                "Task": task.name,
                "Duration (min)": task.duration,
                "Priority": task.priority.name.capitalize(),
                "Frequency": task.frequency.value,
            }
            for pet in owner.pets
            for task in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(f"Pending tasks of all pets, most important first, starting at {DAY_START:%H:%M}.")

if st.button("Generate schedule"):
    schedule = Scheduler(owner).generate_daily_schedule()
    if schedule:
        start = datetime.combine(date.today(), DAY_START)
        rows = []
        for task in schedule:
            end = start + timedelta(minutes=task.duration)
            rows.append(
                {
                    "Time": f"{start:%H:%M}-{end:%H:%M}",
                    "Task": task.name,
                    "Pet": task.pet.name if task.pet else "-",
                    "Priority": task.priority.name.capitalize(),
                    "Frequency": task.frequency.value,
                }
            )
            start = end
        st.table(rows)
    else:
        st.info("Nothing to schedule yet. Add a pet and a task first.")
