import pytest
from datetime import datetime
from pawpal_system import Pet, Task, TaskStatus, Frequency, Priority


# --- Fixtures ---

@pytest.fixture
def sample_pet():
    return Pet(
        pet_id="pet_001",
        name="Mochi",
        species="dog",
        breed="Shiba Inu",
        age=3,
        weight=10.5,
    )


@pytest.fixture
def sample_task(sample_pet):
    return Task(
        task_id="task_001",
        title="Morning Walk",
        description="Walk around the block",
        due_date=datetime(2026, 4, 1, 8, 0),
        assigned_pet=sample_pet,
        duration_minutes=30,
        priority=Priority.HIGH,
        frequency=Frequency.ONCE,
    )


# --- Tests ---

class TestTaskCompletion:
    def test_complete_changes_status_to_completed(self, sample_task):
        assert sample_task.status == TaskStatus.PENDING
        sample_task.complete()
        assert sample_task.status == TaskStatus.COMPLETED

    def test_complete_recurring_task_stays_pending(self, sample_pet):
        """Recurring tasks should reset to PENDING after completion, not stay COMPLETED."""
        task = Task(
            task_id="task_002",
            title="Daily Feeding",
            description="Morning meal",
            due_date=datetime(2026, 4, 1, 7, 0),
            assigned_pet=sample_pet,
            frequency=Frequency.DAILY,
        )
        task.complete()
        assert task.status == TaskStatus.PENDING


class TestTaskAddition:
    def test_add_task_increases_pet_task_count(self, sample_pet, sample_task):
        assert len(sample_pet.tasks) == 0
        sample_pet.add_task(sample_task)
        assert len(sample_pet.tasks) == 1

    def test_add_multiple_tasks_tracks_all(self, sample_pet, sample_task):
        second_task = Task(
            task_id="task_003",
            title="Evening Walk",
            description="Walk before bed",
            due_date=datetime(2026, 4, 1, 20, 0),
            assigned_pet=sample_pet,
        )
        sample_pet.add_task(sample_task)
        sample_pet.add_task(second_task)
        assert len(sample_pet.tasks) == 2
