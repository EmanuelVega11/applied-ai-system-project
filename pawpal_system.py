from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


# --- Enumerations ---

class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# --- Supporting Classes ---

@dataclass
class MedicalRecord:
    record_id: str
    date: datetime
    vet_name: str
    description: str
    notes: str = ""


@dataclass
class Notification:
    notification_id: str
    message: str
    scheduled_time: datetime
    sent: bool = False

    def send(self) -> None:
        self.sent = True
        print(f"[Notification] {self.message} (scheduled: {self.scheduled_time})")

    def cancel(self) -> None:
        self.sent = False


# --- Core Classes ---

@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    medical_history: list[MedicalRecord] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task directly to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def add_medical_record(self, record: MedicalRecord) -> None:
        self.medical_history.append(record)

    def get_medical_history(self) -> list[MedicalRecord]:
        return self.medical_history


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    due_date: datetime
    assigned_pet: Pet
    duration_minutes: int = 30
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    frequency: Frequency = Frequency.ONCE
    notifications: list[Notification] = field(default_factory=list)

    def complete(self) -> None:
        """Mark task complete and auto-schedule the next occurrence for recurring tasks."""
        self.status = TaskStatus.COMPLETED
        if self.frequency == Frequency.DAILY:
            self.due_date += timedelta(days=1)
            self.status = TaskStatus.PENDING
        elif self.frequency == Frequency.WEEKLY:
            self.due_date += timedelta(weeks=1)
            self.status = TaskStatus.PENDING
        elif self.frequency == Frequency.MONTHLY:
            self.due_date += timedelta(days=30)
            self.status = TaskStatus.PENDING

    def reschedule(self, new_date: datetime) -> None:
        """Move the task to a new date and reset overdue status."""
        self.due_date = new_date
        if self.status == TaskStatus.OVERDUE:
            self.status = TaskStatus.PENDING

    def cancel(self) -> None:
        self.status = TaskStatus.CANCELLED

    def is_overdue(self) -> bool:
        return (
            self.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
            and self.due_date < datetime.now()
        )


# --- Scheduler ---

class Scheduler:
    def __init__(self, scheduler_id: str) -> None:
        self.scheduler_id = scheduler_id
        self.tasks: list[Task] = []

    def load_tasks_from_owner(self, owner: Owner) -> None:
        """
        Pull every task from every pet the owner has and add any
        not already tracked by this scheduler.
        """
        tracked_ids = {t.task_id for t in self.tasks}
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                if task.task_id not in tracked_ids:
                    self.tasks.append(task)
                    tracked_ids.add(task.task_id)

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler (and sync it to the assigned pet)."""
        if not any(t.task_id == task.task_id for t in self.tasks):
            self.tasks.append(task)
        if task not in task.assigned_pet.tasks:
            task.assigned_pet.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def check_conflicts(self) -> list[str]:
        """Scan all active tasks for time-window overlaps and return warning messages.

        Compares every pair of non-cancelled, non-completed tasks using an
        interval overlap test: two tasks conflict when
        ``A.start < B.end and B.start < A.end``. This detects partial overlaps,
        full containment, and exact same-start collisions without raising
        exceptions — callers receive warnings and decide how to present them.

        Two severity levels are reported:
            - ``[CONFLICT - SAME PET]``: the same pet is double-booked (hard conflict).
            - ``[CONFLICT - OWNER]``: different pets share the owner's time slot
              (soft conflict — the owner cannot attend both simultaneously).

        Returns:
            list[str]: Human-readable warning strings, one per conflicting pair.
                Returns an empty list when no conflicts exist.

        Example::

            warnings = scheduler.check_conflicts()
            for w in warnings:
                print(w)
        """
        warnings: list[str] = []
        active = [
            t for t in self.tasks
            if t.status not in (TaskStatus.CANCELLED, TaskStatus.COMPLETED)
        ]

        for i, a in enumerate(active):
            for b in active[i + 1:]:
                a_start = a.due_date
                a_end   = a_start + timedelta(minutes=a.duration_minutes)
                b_start = b.due_date
                b_end   = b_start + timedelta(minutes=b.duration_minutes)

                if a_start < b_end and b_start < a_end:
                    a_time = a_start.strftime("%I:%M %p")
                    b_time = b_start.strftime("%I:%M %p")
                    if a.assigned_pet.pet_id == b.assigned_pet.pet_id:
                        warnings.append(
                            f"[CONFLICT - SAME PET]  '{a.title}' ({a_time}, "
                            f"{a.duration_minutes} min) overlaps "
                            f"'{b.title}' ({b_time}, {b.duration_minutes} min) "
                            f"-- both assigned to {a.assigned_pet.name}"
                        )
                    else:
                        warnings.append(
                            f"[CONFLICT - OWNER]     '{a.title}' for "
                            f"{a.assigned_pet.name} ({a_time}, {a.duration_minutes} min) "
                            f"overlaps '{b.title}' for "
                            f"{b.assigned_pet.name} ({b_time}, {b.duration_minutes} min)"
                        )

        return warnings

    def sync_overdue(self) -> None:
        """Scan all tasks and flag any that have passed their due date."""
        for task in self.tasks:
            if task.is_overdue():
                task.status = TaskStatus.OVERDUE

    def get_upcoming_tasks(self, within_hours: int = 24) -> list[Task]:
        """Return pending tasks due within the next N hours, sorted by due date."""
        self.sync_overdue()
        cutoff = datetime.now() + timedelta(hours=within_hours)
        return sorted(
            [
                t for t in self.tasks
                if t.status == TaskStatus.PENDING and datetime.now() <= t.due_date <= cutoff
            ],
            key=lambda t: t.due_date,
        )

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        """Return all tasks assigned to a specific pet, sorted by due date."""
        return sorted(
            [t for t in self.tasks if t.assigned_pet.pet_id == pet_id],
            key=lambda t: t.due_date,
        )

    def get_overdue_tasks(self) -> list[Task]:
        """Return all overdue tasks sorted by how late they are (oldest first)."""
        self.sync_overdue()
        return sorted(
            [t for t in self.tasks if t.status == TaskStatus.OVERDUE],
            key=lambda t: t.due_date,
        )

    def get_tasks_by_priority(self, priority: Priority) -> list[Task]:
        """Return all active tasks matching a given priority level."""
        return [
            t for t in self.tasks
            if t.priority == priority and t.status == TaskStatus.PENDING
        ]

    def filter_tasks(
        self,
        status: TaskStatus | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by status and/or pet name.

        Both parameters are optional. When both are provided the filters are
        applied sequentially (status first, then pet name), so the result
        satisfies *all* supplied criteria. Omitting a parameter disables that
        filter entirely.

        Args:
            status (TaskStatus | None): When provided, only tasks whose
                ``status`` attribute equals this value are returned.
                For example, ``TaskStatus.PENDING`` or ``TaskStatus.COMPLETED``.
                Defaults to ``None`` (no status filter).
            pet_name (str | None): When provided, only tasks whose assigned
                pet name *contains* this string are returned. The match is
                case-insensitive and partial, so ``"mo"`` matches ``"Mochi"``.
                Defaults to ``None`` (no pet-name filter).

        Returns:
            list[Task]: Tasks that satisfy all supplied filters, in their
                current scheduler order (unsorted). Pass the result to
                ``sort_by_time()`` to order chronologically.

        Example::

            # All completed tasks
            scheduler.filter_tasks(status=TaskStatus.COMPLETED)

            # Pending tasks for any pet whose name contains "luna"
            scheduler.filter_tasks(status=TaskStatus.PENDING, pet_name="luna")
        """
        result = self.tasks

        if status is not None:
            result = [t for t in result if t.status == status]

        if pet_name is not None:
            query = pet_name.lower()
            result = [t for t in result if query in t.assigned_pet.name.lower()]

        return result

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks sorted chronologically by time-of-day, with priority as a tiebreaker.

        Sorting is performed on the ``HH:MM`` portion of each task's
        ``due_date``. Because the format is zero-padded and fixed-width,
        lexicographic string comparison produces correct chronological order
        (e.g. ``"07:30" < "08:00" < "18:00"``). When two tasks share the
        same start time, ``HIGH`` priority tasks are listed before ``MEDIUM``
        and ``LOW``.

        Args:
            tasks (list[Task] | None): The list of tasks to sort. When
                ``None``, all tasks currently held by the scheduler are used.
                Pass a pre-filtered list (e.g. from ``filter_tasks()``) to
                sort a subset without modifying the scheduler's internal state.
                Defaults to ``None``.

        Returns:
            list[Task]: A new sorted list. The scheduler's internal task list
                is not modified.

        Example::

            # Sort all scheduler tasks
            scheduler.sort_by_time()

            # Filter then sort — chain the two methods
            pending = scheduler.filter_tasks(status=TaskStatus.PENDING)
            scheduler.sort_by_time(tasks=pending)
        """
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        source = tasks if tasks is not None else self.tasks
        return sorted(
            source,
            key=lambda t: (t.due_date.strftime("%H:%M"), priority_order.get(t.priority, 1)),
        )

    def send_reminders(self, lookahead_minutes: int = 60) -> None:
        """Fire unsent notifications for tasks due within the lookahead window."""
        cutoff = datetime.now() + timedelta(minutes=lookahead_minutes)
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            for notification in task.notifications:
                if not notification.sent and notification.scheduled_time <= cutoff:
                    notification.send()

    def apply_ai_resolution(self, resolution: dict[str, str]) -> None:
        """Apply AI-proposed start times returned by generate_conflict_resolution().

        Args:
            resolution: Mapping of task_id -> "HH:MM" new start time (24-hour).
                        Task IDs not present in the dict are left unchanged.
        """
        for task in self.tasks:
            new_time_str = resolution.get(task.task_id)
            if new_time_str is None:
                continue
            try:
                hour, minute = map(int, new_time_str.split(":"))
                new_dt = task.due_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                task.reschedule(new_dt)
            except (ValueError, AttributeError):
                continue


# --- Owner ---

class Owner:
    def __init__(
        self,
        owner_id: str,
        name: str,
        email: str,
        phone: str,
    ) -> None:
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []
        self.scheduler = Scheduler(scheduler_id=f"sched_{owner_id}")

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_pets(self) -> list[Pet]:
        return self.pets

    def add_task_for_pet(self, task: Task) -> None:
        """Add a task via the scheduler — keeps pet and scheduler in sync."""
        self.scheduler.add_task(task)

    def view_schedule(self) -> list[Task]:
        """Return all tasks across all pets, sorted by due date."""
        self.scheduler.load_tasks_from_owner(self)
        return sorted(self.scheduler.tasks, key=lambda t: t.due_date)
