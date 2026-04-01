import pytest
from datetime import datetime, timedelta
from pawpal_system import Pet, Task, TaskStatus, Frequency, Priority, Scheduler


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


# --- New Tests ---

class TestSortingCorrectness:
    """Verify sort_by_time() returns tasks in chronological order."""

    def test_tasks_sorted_chronologically(self, sample_pet):
        # Three tasks at different times, added out of order
        t1 = Task("s1", "Dinner",    "", datetime(2026, 4, 1, 18, 0), sample_pet)
        t2 = Task("s2", "Breakfast", "", datetime(2026, 4, 1,  7, 0), sample_pet)
        t3 = Task("s3", "Lunch",     "", datetime(2026, 4, 1, 12, 0), sample_pet)

        scheduler = Scheduler("sched_sort")
        for task in (t1, t2, t3):
            scheduler.add_task(task)

        result = scheduler.sort_by_time()

        # Expect 07:00 → 12:00 → 18:00
        assert [t.title for t in result] == ["Breakfast", "Lunch", "Dinner"]

    def test_same_time_high_priority_first(self, sample_pet):
        # Two tasks at the same start time; HIGH should beat MEDIUM
        low_task  = Task("s4", "Low Task",  "", datetime(2026, 4, 1, 9, 0), sample_pet,
                         priority=Priority.LOW)
        high_task = Task("s5", "High Task", "", datetime(2026, 4, 1, 9, 0), sample_pet,
                         priority=Priority.HIGH)

        scheduler = Scheduler("sched_tie")
        scheduler.add_task(low_task)
        scheduler.add_task(high_task)

        result = scheduler.sort_by_time()
        assert result[0].title == "High Task"
        assert result[1].title == "Low Task"


class TestRecurrenceLogic:
    """Confirm that completing a recurring task advances its due_date."""

    def test_daily_task_advances_one_day(self, sample_pet):
        original_date = datetime(2026, 4, 1, 7, 0)
        task = Task(
            task_id="r1",
            title="Daily Feeding",
            description="Morning meal",
            due_date=original_date,
            assigned_pet=sample_pet,
            frequency=Frequency.DAILY,
        )
        task.complete()

        # Status resets to PENDING and date moves forward exactly 1 day
        assert task.status == TaskStatus.PENDING
        assert task.due_date == original_date + timedelta(days=1)

    def test_weekly_task_advances_seven_days(self, sample_pet):
        original_date = datetime(2026, 4, 1, 10, 0)
        task = Task(
            task_id="r2",
            title="Weekly Bath",
            description="Grooming",
            due_date=original_date,
            assigned_pet=sample_pet,
            frequency=Frequency.WEEKLY,
        )
        task.complete()

        assert task.status == TaskStatus.PENDING
        assert task.due_date == original_date + timedelta(weeks=1)

    def test_once_task_stays_completed(self, sample_pet):
        task = Task(
            task_id="r3",
            title="Vet Visit",
            description="Annual checkup",
            due_date=datetime(2026, 4, 1, 14, 0),
            assigned_pet=sample_pet,
            frequency=Frequency.ONCE,
        )
        task.complete()

        assert task.status == TaskStatus.COMPLETED


class TestConflictDetection:
    """Verify Scheduler.check_conflicts() correctly flags overlapping tasks."""

    def test_no_conflict_when_tasks_dont_overlap(self, sample_pet):
        # 08:00–08:30 and 09:00–09:30 — gap between them, no conflict
        t1 = Task("c1", "Walk",    "", datetime(2026, 4, 1, 8,  0), sample_pet, duration_minutes=30)
        t2 = Task("c2", "Feeding", "", datetime(2026, 4, 1, 9,  0), sample_pet, duration_minutes=30)

        scheduler = Scheduler("sched_no_conflict")
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        assert scheduler.check_conflicts() == []

    def test_same_pet_overlap_flagged(self, sample_pet):
        # 08:00–08:30 and 08:15–08:45 — 15-minute overlap, same pet
        t1 = Task("c3", "Walk",     "", datetime(2026, 4, 1, 8,  0), sample_pet, duration_minutes=30)
        t2 = Task("c4", "Feeding",  "", datetime(2026, 4, 1, 8, 15), sample_pet, duration_minutes=30)

        scheduler = Scheduler("sched_same_pet")
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        warnings = scheduler.check_conflicts()
        assert len(warnings) == 1
        assert "[CONFLICT - SAME PET]" in warnings[0]

    def test_exact_same_start_time_flagged(self, sample_pet):
        # Two tasks starting at exactly the same time — hard collision
        t1 = Task("c5", "Walk",    "", datetime(2026, 4, 1, 9, 0), sample_pet, duration_minutes=30)
        t2 = Task("c6", "Feeding", "", datetime(2026, 4, 1, 9, 0), sample_pet, duration_minutes=30)

        scheduler = Scheduler("sched_exact")
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        warnings = scheduler.check_conflicts()
        assert len(warnings) == 1
        assert "[CONFLICT - SAME PET]" in warnings[0]

    def test_different_pets_owner_conflict_flagged(self, sample_pet):
        # Two different pets, overlapping slots — owner can't attend both
        other_pet = Pet("pet_002", "Luna", "cat", "Siamese", 2, 4.0)

        t1 = Task("c7", "Walk",   "", datetime(2026, 4, 1, 10,  0), sample_pet, duration_minutes=30)
        t2 = Task("c8", "Grooming", "", datetime(2026, 4, 1, 10, 15), other_pet,  duration_minutes=30)

        scheduler = Scheduler("sched_owner")
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        warnings = scheduler.check_conflicts()
        assert len(warnings) == 1
        assert "[CONFLICT - OWNER]" in warnings[0]

    def test_completed_tasks_excluded_from_conflict_check(self, sample_pet):
        # A completed task should not trigger a conflict even if times overlap
        t1 = Task("c9",  "Walk",    "", datetime(2026, 4, 1, 8, 0), sample_pet, duration_minutes=30)
        t2 = Task("c10", "Feeding", "", datetime(2026, 4, 1, 8, 0), sample_pet, duration_minutes=30)
        t1.complete()  # ONCE task → COMPLETED

        scheduler = Scheduler("sched_completed")
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        assert scheduler.check_conflicts() == []
