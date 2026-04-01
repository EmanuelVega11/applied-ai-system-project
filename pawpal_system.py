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

    def send_reminders(self, lookahead_minutes: int = 60) -> None:
        """Fire unsent notifications for tasks due within the lookahead window."""
        cutoff = datetime.now() + timedelta(minutes=lookahead_minutes)
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            for notification in task.notifications:
                if not notification.sent and notification.scheduled_time <= cutoff:
                    notification.send()


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
