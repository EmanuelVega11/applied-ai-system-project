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

## Features

- **Chronological sorting** — `sort_by_time()` orders tasks by `HH:MM`; ties broken by priority (HIGH first).
- **Composable filters** — `filter_tasks(status, pet_name)` supports exact status matching and partial, case-insensitive pet name search. Chain with `sort_by_time()` to filter then sort.
- **Conflict detection** — `check_conflicts()` uses an interval overlap test (`A.start < B.end and B.start < A.end`) to catch partial overlaps, full containment, and exact same-start collisions. Returns plain-English warnings at two severity levels: same-pet double-bookings (hard conflict) and owner time clashes across different pets (soft conflict).
- **Recurring task recurrence** — `Task.complete()` auto-advances `due_date` by the task's frequency (daily +1 day, weekly +7 days, monthly +30 days) and resets status to `PENDING`. One-time tasks stay `COMPLETED`.
- **Overdue sync** — `sync_overdue()` scans all tasks and promotes past-due pending tasks to `OVERDUE`. Completed and cancelled tasks are never affected.
- **Upcoming task window** — `get_upcoming_tasks(within_hours)` returns pending tasks due within the next N hours, sorted by due date.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run tests

```bash
python -m pytest
```

All 14 tests pass, covering sorting correctness, recurrence logic, and conflict detection.

