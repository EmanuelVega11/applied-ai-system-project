from datetime import datetime
from pawpal_system import Owner, Pet, Task, TaskStatus, Frequency, Priority

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

# --- Tasks added OUT OF ORDER (intentionally scrambled times) ---
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

afternoon_nap_check = Task(
    task_id="task_005",
    title="Nap Check",
    description="Check Luna's sleeping spot and refill water",
    due_date=today.replace(hour=13, minute=15),
    assigned_pet=luna,
    duration_minutes=5,
    priority=Priority.LOW,
    frequency=Frequency.DAILY,
)

vet_checkup = Task(
    task_id="task_006",
    title="Vet Checkup",
    description="Annual wellness exam",
    due_date=today.replace(hour=9, minute=0),
    assigned_pet=mochi,
    duration_minutes=60,
    priority=Priority.HIGH,
    frequency=Frequency.ONCE,
)

# --- Conflict tasks (deliberate scheduling collisions) ---

# SAME-PET conflict: Mochi has a 60-min Vet Checkup at 09:00
# and a 30-min Grooming starting at 09:20 -- windows overlap
grooming = Task(
    task_id="task_007",
    title="Grooming",
    description="Bath and brush for Mochi",
    due_date=today.replace(hour=9, minute=20),
    assigned_pet=mochi,
    duration_minutes=30,
    priority=Priority.MEDIUM,
    frequency=Frequency.ONCE,
)

# OWNER conflict: Luna's Feeding starts at 08:00 (5 min)
# and Luna's Medication starts at 08:03 -- overlaps within the same window
luna_medication = Task(
    task_id="task_008",
    title="Medication",
    description="Give Luna her daily thyroid pill",
    due_date=today.replace(hour=8, minute=3),
    assigned_pet=luna,
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
)

# Added out of order: 18:00, 10:00, 08:00, 07:30, 13:15, 09:00, 09:20, 08:03
owner.add_task_for_pet(evening_playtime)
owner.add_task_for_pet(flea_treatment)
owner.add_task_for_pet(feeding)
owner.add_task_for_pet(morning_walk)
owner.add_task_for_pet(afternoon_nap_check)
owner.add_task_for_pet(vet_checkup)
owner.add_task_for_pet(grooming)
owner.add_task_for_pet(luna_medication)

# Mark vet checkup completed so filtering by status has something to show
vet_checkup.complete()

scheduler = owner.scheduler
scheduler.load_tasks_from_owner(owner)

# ── Helper ───────────────────────────────────────────────────────────────────

def print_tasks(tasks, title):
    print()
    print("=" * 52)
    print(f"  {title}")
    print("=" * 52)
    if not tasks:
        print("  (no tasks match)")
    for task in tasks:
        time_str  = task.due_date.strftime("%I:%M %p")
        status    = task.status.value.upper()
        priority  = task.priority.value.capitalize()
        pet       = task.assigned_pet.name
        print(
            f"  {time_str}  |  {task.title:<22}|  {pet:<6}"
            f"  |  {priority:<6}  |  [{status}]"
        )
    print(f"  {len(tasks)} task(s)")
    print("=" * 52)

# ── 1. sort_by_time() — all tasks, chronological ─────────────────────────────
sorted_all = scheduler.sort_by_time()
print_tasks(sorted_all, "sort_by_time()  —  all tasks (added out of order, now sorted)")

# ── 2. filter_tasks(status=PENDING) ──────────────────────────────────────────
pending = scheduler.filter_tasks(status=TaskStatus.PENDING)
print_tasks(pending, "filter_tasks(status=PENDING)")

# ── 3. filter_tasks(status=COMPLETED) ────────────────────────────────────────
completed = scheduler.filter_tasks(status=TaskStatus.COMPLETED)
print_tasks(completed, "filter_tasks(status=COMPLETED)")

# ── 4. filter_tasks(pet_name="luna") — partial, case-insensitive ─────────────
luna_tasks = scheduler.filter_tasks(pet_name="luna")
print_tasks(luna_tasks, 'filter_tasks(pet_name="luna")')

# ── 5. filter_tasks(pet_name="mo") — partial match finds "Mochi" ─────────────
mochi_tasks = scheduler.filter_tasks(pet_name="mo")
print_tasks(mochi_tasks, 'filter_tasks(pet_name="mo")  -- partial match -> Mochi')

# ── 6. Combined: pending tasks for Luna, sorted by time ──────────────────────
luna_pending = scheduler.filter_tasks(status=TaskStatus.PENDING, pet_name="luna")
sorted_luna  = scheduler.sort_by_time(tasks=luna_pending)
print_tasks(sorted_luna, 'filter_tasks(PENDING, "luna")  ->  sort_by_time()')

# ── 7. check_conflicts() — detect overlapping task windows ───────────────────
print()
print("=" * 52)
print("  check_conflicts()  --  scanning for overlaps")
print("=" * 52)
conflicts = scheduler.check_conflicts()
if not conflicts:
    print("  No conflicts detected.")
else:
    for warning in conflicts:
        print(f"  {warning}")
print(f"  {len(conflicts)} conflict(s) found")
print("=" * 52)
