from __future__ import annotations

import json
import os

import anthropic

from pawpal_system import Task


_SYSTEM_PROMPT = (
    "You are an expert pet-care scheduler. Your sole job is to resolve scheduling "
    "conflicts by proposing new start times that eliminate all time-window overlaps.\n\n"
    "Rules you MUST follow:\n"
    "1. HIGH priority tasks must stay as close as possible to their original start time. "
    "Prefer shifting MEDIUM or LOW priority tasks to accommodate them.\n"
    "2. No two tasks may overlap. Two tasks overlap when one starts before the other ends. "
    "Each task's window is: start_time to start_time + duration_minutes.\n"
    "3. All proposed times must fall within a realistic pet-care day: 06:00 to 22:00.\n"
    "4. Preserve the relative ordering of tasks where possible — an earlier task should "
    "remain earlier than a later task, unless priority demands otherwise.\n"
    "5. Leave at least 5 minutes of buffer between consecutive tasks.\n\n"
    "Output format — respond with ONLY a valid JSON object, no markdown, no explanation:\n"
    '{\n  "<task_id>": "<HH:MM>",\n  "<task_id>": "<HH:MM>"\n}\n\n'
    "The keys are the exact task_id strings provided. "
    "The values are 24-hour HH:MM strings (e.g. \"09:30\", \"14:05\"). "
    "Do not include any other text outside the JSON object."
)


def generate_conflict_resolution(conflicting_tasks: list[Task]) -> dict:
    """
    Ask Claude to propose non-overlapping start times for a set of conflicting tasks.

    Returns a dict mapping task_id -> "HH:MM" proposed start time.
    Returns an empty dict if the task list is empty, the API call fails,
    or the response cannot be parsed as valid JSON.

    Requires the ANTHROPIC_API_KEY environment variable to be set.
    """
    if not conflicting_tasks:
        return {}

    task_summaries = [
        {
            "task_id": task.task_id,
            "title": task.title,
            "duration_minutes": task.duration_minutes,
            "priority": task.priority.value,
            "current_due_date": task.due_date.strftime("%Y-%m-%d %H:%M"),
        }
        for task in conflicting_tasks
    ]

    user_content = (
        "The following tasks are in conflict — their time windows overlap. "
        "Propose new, non-overlapping start times for each task.\n\n"
        f"Tasks:\n{json.dumps(task_summaries, indent=2)}"
    )

    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )

        text_block = next(
            (block for block in response.content if block.type == "text"), None
        )
        if text_block is None:
            return {}
        raw = text_block.text.strip()
        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()
        return json.loads(raw)

    except (anthropic.APIError, json.JSONDecodeError, IndexError, KeyError):
        return {}
