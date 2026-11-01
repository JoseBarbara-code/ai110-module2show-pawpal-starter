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

The demo script `main.py` builds a sample owner with two pets and seven tasks, then prints today's schedule in the terminal (no Streamlit needed):

```bash
python main.py
```

Actual output:

```
Today's Schedule for Jordan
Pets: Mochi (dog), Luna (cat)
Time available: 60 min
==================================================
#   Task                Pet      Minutes  Priority
--------------------------------------------------
1   Breakfast           Luna           5  high
2   Breakfast           Mochi         10  high
3   Morning walk        Mochi         30  high
4   Brush fur           Luna          10  medium
--------------------------------------------------
Time used: 55 min | Time left: 5 min
Order: highest priority first, shorter tasks first when tied.

Skipped (not enough time left):
  - Bath (Mochi) - 40 min, medium priority
  - Fetch in the yard (Mochi) - 15 min, low priority
  - Laser pointer play (Luna) - 15 min, low priority
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output from `py -m pytest -v` (header lines with local folder paths left out):

```
collected 6 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 16%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 33%]
tests/test_pawpal.py::test_high_priority_tasks_come_first PASSED         [ 50%]
tests/test_pawpal.py::test_plan_fits_in_available_time PASSED            [ 66%]
tests/test_pawpal.py::test_completed_tasks_are_not_scheduled PASSED      [ 83%]
tests/test_pawpal.py::test_get_all_tasks_collects_from_every_pet PASSED  [100%]

============================== 6 passed in 0.04s ==============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
