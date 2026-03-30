from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
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
        pass

    def cancel(self) -> None:
        pass


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

    def add_medical_record(self, record: MedicalRecord) -> None:
        pass

    def get_medical_history(self) -> list[MedicalRecord]:
        return self.medical_history


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    due_date: datetime
    assigned_pet: Pet
    status: TaskStatus = TaskStatus.PENDING
    frequency: Frequency = Frequency.ONCE
    notifications: list[Notification] = field(default_factory=list)

    def complete(self) -> None:
        pass

    def reschedule(self, new_date: datetime) -> None:
        pass

    def cancel(self) -> None:
        pass


class Scheduler:
    def __init__(self, scheduler_id: str) -> None:
        self.scheduler_id = scheduler_id
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_upcoming_tasks(self) -> list[Task]:
        return []

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        return []

    def get_overdue_tasks(self) -> list[Task]:
        return []

    def send_reminders(self) -> None:
        pass


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
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        return self.pets

    def view_schedule(self) -> list[Task]:
        return self.scheduler.tasks
