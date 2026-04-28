"""Pytest suite for AI-integrated scheduler functionality.

Mocks the Anthropic API so tests run locally without an API key.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from unittest.mock import MagicMock, patch

from pawpal_system import Frequency, Pet, Priority, Scheduler, Task, TaskStatus
from ai_agent import generate_conflict_resolution


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_pet(pet_id: str = "pet_001", name: str = "Mochi") -> Pet:
    return Pet(
        pet_id=pet_id,
        name=name,
        species="dog",
        breed="Shiba Inu",
        age=3,
        weight=10.5,
    )


def _make_task(
    task_id: str,
    pet: Pet,
    hour: int = 9,
    minute: int = 0,
) -> Task:
    return Task(
        task_id=task_id,
        title="Morning walk",
        description="Walk around the block",
        due_date=datetime(2026, 4, 27, hour, minute),
        assigned_pet=pet,
        duration_minutes=30,
        priority=Priority.MEDIUM,
        status=TaskStatus.PENDING,
        frequency=Frequency.ONCE,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestApplyAIResolution:

    def test_valid_resolution_updates_task_time(self):
        """apply_ai_resolution should reschedule a task when given a valid task_id -> HH:MM dict."""
        pet = _make_pet()
        task = _make_task("task_001", pet, hour=9, minute=0)
        scheduler = Scheduler("sched_001")
        scheduler.add_task(task)

        scheduler.apply_ai_resolution({"task_001": "14:30"})

        assert task.due_date.hour == 14
        assert task.due_date.minute == 30
        # Date portion must be unchanged
        assert task.due_date.date() == datetime(2026, 4, 27).date()

    def test_markdown_wrapped_json_is_cleaned_and_parsed(self):
        """generate_conflict_resolution must strip ```json fences before JSON-parsing the response."""
        pet = _make_pet()
        task = _make_task("task_001", pet)

        # Simulate an LLM that wraps its JSON in markdown code fences
        markdown_response = '```json\n{"task_001": "14:30"}\n```'

        fake_block = MagicMock()
        fake_block.type = "text"
        fake_block.text = markdown_response

        fake_response = MagicMock()
        fake_response.content = [fake_block]

        with patch("ai_agent.anthropic.Anthropic") as mock_anthropic_cls:
            mock_client = MagicMock()
            mock_anthropic_cls.return_value = mock_client
            mock_client.messages.create.return_value = fake_response

            result = generate_conflict_resolution([task])

        assert result == {"task_001": "14:30"}

    def test_empty_dict_fallback_leaves_tasks_unchanged(self):
        """apply_ai_resolution({}) must not raise and must leave every task's time intact."""
        pet = _make_pet()
        task = _make_task("task_001", pet, hour=10, minute=15)
        original_due = task.due_date

        scheduler = Scheduler("sched_001")
        scheduler.add_task(task)

        # Should not raise even when no resolution is provided
        scheduler.apply_ai_resolution({})

        assert task.due_date == original_due
        assert task.status == TaskStatus.PENDING
