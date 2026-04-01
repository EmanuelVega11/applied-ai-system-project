import uuid
from datetime import datetime
import streamlit as st
from pawpal_system import Owner, Pet, Task, Frequency, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session State: persist Owner across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id="owner_001",
        name="Jordan",
        email="",
        phone="",
    )

owner: Owner = st.session_state.owner

# ── Section 1: Add a Pet ──────────────────────────────────────────────────────
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed", value="Shiba Inu")

col4, col5 = st.columns(2)
with col4:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
with col5:
    weight = st.number_input("Weight (lbs)", min_value=0.1, max_value=300.0, value=10.5)

if st.button("Add Pet"):
    # owner.add_pet() is the method from Phase 2 that appends to owner.pets
    new_pet = Pet(
        pet_id=str(uuid.uuid4()),
        name=pet_name,
        species=species,
        breed=breed,
        age=int(age),
        weight=float(weight),
    )
    owner.add_pet(new_pet)
    st.success(f"{pet_name} added!")

# Show current pets so the user sees the update immediately
pets = owner.get_pets()
if pets:
    st.write("**Your pets:**")
    st.table([
        {"Name": p.name, "Species": p.species, "Breed": p.breed,
         "Age": p.age, "Weight (lbs)": p.weight}
        for p in pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Section 2: Schedule a Task ───────────────────────────────────────────────
st.subheader("Schedule a Task")

if not pets:
    st.warning("Add at least one pet before scheduling a task.")
else:
    pet_names = [p.name for p in pets]

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    with col2:
        task_desc = st.text_input("Description", value="Walk around the block")
        priority_str = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency_str = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"])
        due_time = st.time_input("Due time", value=datetime.now().replace(second=0, microsecond=0))

    if st.button("Add Task"):
        # Look up the Pet object the user selected
        assigned_pet = next(p for p in pets if p.name == selected_pet_name)

        new_task = Task(
            task_id=str(uuid.uuid4()),
            title=task_title,
            description=task_desc,
            due_date=datetime.combine(datetime.today(), due_time),
            assigned_pet=assigned_pet,
            duration_minutes=int(duration),
            priority=Priority(priority_str),
            frequency=Frequency(frequency_str),
        )

        # owner.add_task_for_pet() syncs the task to both the pet and the scheduler
        owner.add_task_for_pet(new_task)
        st.success(f'"{task_title}" scheduled for {selected_pet_name}!')

st.divider()

# ── Section 3: Today's Schedule ──────────────────────────────────────────────
st.subheader("Today's Schedule")

if st.button("Generate Schedule"):
    # owner.view_schedule() calls scheduler.load_tasks_from_owner() internally
    # and returns all tasks sorted by due date
    schedule = owner.view_schedule()

    if not schedule:
        st.info("No tasks scheduled yet.")
    else:
        st.table([
            {
                "Time": t.due_date.strftime("%I:%M %p"),
                "Task": t.title,
                "Pet": t.assigned_pet.name,
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority.value.capitalize(),
                "Frequency": t.frequency.value.capitalize(),
                "Status": t.status.value.upper(),
            }
            for t in schedule
        ])
        st.caption(f"{len(schedule)} task(s) across {len(pets)} pet(s)")
