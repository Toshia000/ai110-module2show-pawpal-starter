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

## 🖥️ Sample Output

```
Today's Schedule for Jordan Lee - Tuesday, October 20, 2026

Time         Done  Task          Pet    Priority  Frequency
-----------  ----  ------------  -----  --------  ---------
08:00-08:30  [ ]   Morning walk  Mochi  HIGH      daily
08:30-08:40  [ ]   Feeding       Luna   MEDIUM    daily
08:40-09:25  [ ]   Grooming      Mochi  LOW       weekly
```

## Implementation summary

- Owner can have multiple pets
- Pets can be of different species and can have multiple tasks
- Tasks can have different priorities and frequencies
- Scheduler sorts tasks by priority and generates daily schedules

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The `Scheduler` in `pawpal_system.py` goes beyond a simple task list. Run `python main.py` to see each feature in the terminal.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_priority()`, `sort_by_time()` | Priority puts HIGH first. Time sorts earliest first, with untimed tasks last and ties broken by priority. Both are O(n log n). |
| Filtering | `filter_tasks(completed, pet_name)`, `generate_daily_schedule()` | Filter by completion status and/or pet name (case-insensitive); the two combine with AND. The daily schedule keeps only pending tasks due today or earlier. |
| Conflict handling | `find_conflicts()`, `conflict_warnings()` | Detects overlapping time ranges (start plus duration), not just identical start times, for the same pet or different pets. Back-to-back tasks are fine. Returns warning messages instead of raising, so the app keeps running. |
| Recurring tasks | `Task.mark_complete()` | Completing a `daily` or `weekly` task creates the next occurrence on the same pet, due 1 or 7 days after the original. One-off (`once`) tasks and repeat completions create nothing. |

Example conflict warnings:

```
Warning (different pets): Mochi's Medication (14:00-14:10) overlaps Luna's Insulin shot (14:00-14:10)
Warning (same pet): Mochi's Evening walk (18:30-19:00) overlaps Mochi's Vet call (18:45-19:00)
```

### Design tradeoffs

- **Conflicts only warn.** Nothing blocks adding a task, and the owner is assumed to do one thing at a time, so tasks for different pets can conflict too.
- **Only timed, pending tasks are checked.** Completed tasks, untimed tasks and tasks on different days are ignored.
- **The daily schedule ranks by priority only.** It does not yet use `task.time`, and there is no daily time budget, so it never drops tasks.
- **Recurrence counts from the due date.** A task finished late keeps its cadence, so its next copy can already be overdue. Completed copies accumulate in the task list.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
