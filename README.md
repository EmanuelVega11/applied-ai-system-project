# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Three algorithmic methods were added to the `Scheduler` class in `pawpal_system.py` to make the schedule more useful for a real pet owner.

### `sort_by_time(tasks=None)`

Returns tasks sorted chronologically by time-of-day using Python's `sorted()` with a lambda key. The key converts each task's `due_date` to a zero-padded `"HH:MM"` string so lexicographic comparison equals chronological order. A second key breaks ties by priority — `HIGH` tasks appear before `MEDIUM` and `LOW` at the same start time. An optional `tasks` parameter lets you sort any filtered subset without affecting the scheduler's internal state.

### `filter_tasks(status=None, pet_name=None)`

Returns tasks that match all supplied filters. Both parameters are optional and combinable:

- **`status`** — exact match on `TaskStatus` (e.g. `PENDING`, `COMPLETED`)
- **`pet_name`** — case-insensitive partial match on the pet's name (`"mo"` matches `"Mochi"`)

Filters are applied sequentially, so the result satisfies every condition provided. The two methods chain naturally — filter first, then pass the result to `sort_by_time()`.

### `check_conflicts()`

Scans all active (non-cancelled, non-completed) tasks for time-window overlaps using the interval test `A.start < B.end and B.start < A.end`. This catches partial overlaps, full containment, and exact same-start collisions. Instead of raising exceptions, it returns a list of human-readable warning strings so the caller decides how to display them. Two conflict types are reported:

- `[CONFLICT - SAME PET]` — the same pet is double-booked (hard conflict)
- `[CONFLICT - OWNER]` — different pets overlap in the owner's time slot (soft conflict)

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
