from datetime import datetime
from pawpal_system import Owner, Pet, Task, Frequency, Priority

# --- Setup ---
today = datetime.now().replace(second=0, microsecond=0)

owner = Owner(
    owner_id="owner_001",
    name="Jordan",
    email="jordan@email.com",
    phone="555-1234",
)

# --- Pets ---
mochi = Pet(
    pet_id="pet_001",
    name="Mochi",
    species="dog",
    breed="Shiba Inu",
    age=3,
    weight=10.5,
)

luna = Pet(
    pet_id="pet_002",
    name="Luna",
    species="cat",
    breed="Tabby",
    age=5,
    weight=4.2,
)

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks ---
morning_walk = Task(
    task_id="task_001",
    title="Morning Walk",
    description="30-minute walk around the block",
    due_date=today.replace(hour=7, minute=30),
    assigned_pet=mochi,
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
)

feeding = Task(
    task_id="task_002",
    title="Feeding",
    description="Give Luna her wet food (1/2 can)",
    due_date=today.replace(hour=8, minute=0),
    assigned_pet=luna,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
)

flea_treatment = Task(
    task_id="task_003",
    title="Flea Treatment",
    description="Apply monthly flea and tick prevention",
    due_date=today.replace(hour=10, minute=0),
    assigned_pet=mochi,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    frequency=Frequency.MONTHLY,
)

evening_playtime = Task(
    task_id="task_004",
    title="Evening Playtime",
    description="Laser pointer and feather toy session",
    due_date=today.replace(hour=18, minute=0),
    assigned_pet=luna,
    duration_minutes=20,
    priority=Priority.LOW,
    frequency=Frequency.DAILY,
)

owner.add_task_for_pet(morning_walk)
owner.add_task_for_pet(feeding)
owner.add_task_for_pet(flea_treatment)
owner.add_task_for_pet(evening_playtime)

# --- Print Today's Schedule ---
schedule = owner.view_schedule()

print("=" * 45)
print(f"  PawPal+ — Today's Schedule for {owner.name}")
print("=" * 45)

if not schedule:
    print("  No tasks scheduled for today.")
else:
    for task in schedule:
        time_str = task.due_date.strftime("%I:%M %p")
        status_str = task.status.value.upper()
        priority_str = task.priority.value.capitalize()
        print(
            f"  {time_str}  |  {task.title:<22} |  {task.assigned_pet.name:<6}"
            f"  |  {priority_str:<6}  |  [{status_str}]"
        )

print("=" * 45)
print(f"  {len(schedule)} task(s) across {len(owner.get_pets())} pet(s)")
print("=" * 45)
