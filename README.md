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

The demo script `main.py` builds a sample owner (Jordan, 60 free minutes) with two pets and a mix of tasks, then shows, without Streamlit:

- today's schedule (tasks chosen by priority to fit the time, then listed by time of day)
- sorting and filtering examples
- an invalid time being rejected
- recurring tasks being completed
- a conflict check

```bash
python main.py   # or: py main.py on Windows without a virtual environment
```

Actual output from a run on **2026-11-01**. The dates in the "Recurring tasks" and "Conflict check" sections are worked out from the day you run it (today, tomorrow, and one week later), so you'll see different dates:

```
Today's Schedule for Jordan
Pets: Mochi (dog), Luna (cat)
Time available: 60 min
========================================================
Time     Task                Pet      Minutes  Priority
--------------------------------------------------------
07:00    Breakfast           Mochi         10  high
07:30    Morning walk        Mochi         30  high
08:00    Breakfast           Luna           5  high
anytime  Brush fur           Luna          10  medium
--------------------------------------------------------
Time used: 55 min | Time left: 5 min
Tasks are chosen by priority to fit your time, then listed by time of day.

Skipped (not enough time left):
  - Bath (Mochi) - 40 min, medium priority
  - Fetch in the yard (Mochi) - 15 min, low priority
  - Laser pointer play (Luna) - 15 min, low priority

All tasks sorted by time:
  07:00    Breakfast (Mochi) - 10 min, high priority
  07:15    Litter box (Luna) - 5 min, high priority [done]
  07:30    Morning walk (Mochi) - 30 min, high priority
  08:00    Breakfast (Luna) - 5 min, high priority
  17:00    Fetch in the yard (Mochi) - 15 min, low priority
  19:00    Laser pointer play (Luna) - 15 min, low priority
  anytime  Bath (Mochi) - 40 min, medium priority
  anytime  Brush fur (Luna) - 10 min, medium priority

Filter - Mochi's tasks:
  07:00    Breakfast (Mochi) - 10 min, high priority
  07:30    Morning walk (Mochi) - 30 min, high priority
  17:00    Fetch in the yard (Mochi) - 15 min, low priority
  anytime  Bath (Mochi) - 40 min, medium priority

Filter - completed tasks:
  07:15    Litter box (Luna) - 5 min, high priority [done]

Filter - Luna's tasks that aren't done:
  08:00    Breakfast (Luna) - 5 min, high priority
  19:00    Laser pointer play (Luna) - 15 min, low priority
  anytime  Brush fur (Luna) - 10 min, medium priority

Invalid time rejected: Time must be 24-hour HH:MM, like '08:00' or '14:30' (got '25:00').

Recurring tasks:
  Completed Breakfast (daily, due 2026-11-01) -> next one due 2026-11-02
  Completed Bath (weekly, due 2026-11-01) -> next one due 2026-11-08
  Completed Vet visit (once) -> doesn't repeat
  Completed Breakfast again -> Mochi still has 7 tasks (was 7)

Today's plan after completing those tasks:
  07:30    Morning walk (Mochi) - 30 min, high priority
  08:00    Breakfast (Luna) - 5 min, high priority
  17:00    Fetch in the yard (Mochi) - 15 min, low priority
  anytime  Brush fur (Luna) - 10 min, medium priority

Mochi's tasks that aren't done (including future ones):
  07:30    Morning walk (Mochi) - 30 min, high priority
  17:00    Fetch in the yard (Mochi) - 15 min, low priority
  07:00    Breakfast (Mochi) - 10 min, high priority (due 2026-11-02)
  anytime  Bath (Mochi) - 40 min, medium priority (due 2026-11-08)

Conflict check:
  Current tasks:
    No conflicts.
  After adding Medicine (07:30), Training (07:45), and Grooming (07:30 tomorrow):
    WARNING: Conflict at 07:30 on 2026-11-01: Morning walk (Mochi), Medicine (Luna)
  Different times - Morning walk 07:30 vs Training 07:45:
    No conflicts.
  Different dates - Medicine 07:30 today vs Grooming 07:30 tomorrow:
    No conflicts.
```

## 🧪 Testing PawPal+

Run the tests from the project folder:

```bash
python -m pytest       # on Windows without a virtual environment: py -m pytest
python -m pytest -v    # same, but lists every test by name
```

Coverage (`pytest --cov`) needs `pip install pytest-cov`, which is not in `requirements.txt`.

**What the 42 tests cover** (all in `tests/test_pawpal.py`, testing the backend in `pawpal_system.py`):

- **Basic scheduling (6):** completing and adding tasks, higher priority first, the plan never going over the available time, completed tasks left out, and tasks collected from several pets.
- **Sorting and time formats (6):** time order with "anytime" tasks last and earlier dates first, `"8:05"` stored as `"08:05"`, invalid times rejected, and times not changing the priority-based plan.
- **Filtering (4):** by pet name, by completion status, by both, and with no filters.
- **Recurring tasks (12):** daily +1 day, weekly +7 days (including month and year rollover), "once" tasks not repeating, no duplicate copies, late and early completion, and future copies kept out of today's plan.
- **Conflict detection (8):** same time for the same pet or different pets, three tasks in one slot, and no false warnings for different times, different dates, tasks without a time, or completed tasks.
- **Edge cases (6):** an owner with no pets or a pet with no tasks, nothing fitting in the available time, same-priority tasks going shortest first, unpadded times like `"9:00"` sorting correctly, the same time typed two ways (`"8:00"` / `"08:00"`) still conflicting, and the `explain_plan()` text.

Most recurrence tests use fixed dates, and the few that check today's plan use dates relative to today, so the suite gives the same result on any day.

**Confidence level: ★★★★☆ (4/5).** All 42 backend tests pass, including the edge cases above. It isn't 5/5 because the Streamlit UI (`app.py`) has no automated tests, and conflict detection only checks identical start times, so overlapping durations (for example, a 30-minute task at 07:30 and another at 07:45) aren't flagged.

Actual output from `py -m pytest -v` (header lines with local folder paths left out):

```
collected 42 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  2%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  4%]
tests/test_pawpal.py::test_high_priority_tasks_come_first PASSED         [  7%]
tests/test_pawpal.py::test_plan_fits_in_available_time PASSED            [  9%]
tests/test_pawpal.py::test_completed_tasks_are_not_scheduled PASSED      [ 11%]
tests/test_pawpal.py::test_get_all_tasks_collects_from_every_pet PASSED  [ 14%]
tests/test_pawpal.py::test_sort_by_time_orders_earliest_first PASSED     [ 16%]
tests/test_pawpal.py::test_sort_by_time_puts_anytime_tasks_last PASSED   [ 19%]
tests/test_pawpal.py::test_time_is_normalized_to_hh_mm PASSED            [ 21%]
tests/test_pawpal.py::test_invalid_time_raises_error PASSED              [ 23%]
tests/test_pawpal.py::test_times_do_not_change_priority_based_plan PASSED [ 26%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 28%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [ 30%]
tests/test_pawpal.py::test_filter_tasks_by_pet_and_status PASSED         [ 33%]
tests/test_pawpal.py::test_filter_tasks_with_no_filters_returns_everything PASSED [ 35%]
tests/test_pawpal.py::test_daily_task_next_occurrence_is_one_day_later PASSED [ 38%]
tests/test_pawpal.py::test_weekly_task_next_occurrence_is_seven_days_later PASSED [ 40%]
tests/test_pawpal.py::test_next_occurrence_crosses_month_and_year PASSED [ 42%]
tests/test_pawpal.py::test_once_task_does_not_repeat PASSED              [ 45%]
tests/test_pawpal.py::test_complete_task_adds_next_occurrence_to_pet PASSED [ 47%]
tests/test_pawpal.py::test_completing_a_task_twice_does_not_duplicate PASSED [ 50%]
tests/test_pawpal.py::test_late_completion_counts_from_completion_date PASSED [ 52%]
tests/test_pawpal.py::test_early_completion_keeps_the_schedule PASSED    [ 54%]
tests/test_pawpal.py::test_late_completed_task_next_copy_is_not_overdue PASSED [ 57%]
tests/test_pawpal.py::test_frequency_is_checked PASSED                   [ 59%]
tests/test_pawpal.py::test_future_tasks_are_not_in_todays_plan PASSED    [ 61%]
tests/test_pawpal.py::test_completed_daily_task_next_copy_waits_for_tomorrow PASSED [ 64%]
tests/test_pawpal.py::test_sort_by_time_puts_earlier_days_first PASSED   [ 66%]
tests/test_pawpal.py::test_two_tasks_at_same_time_conflict PASSED        [ 69%]
tests/test_pawpal.py::test_conflict_between_different_pets PASSED        [ 71%]
tests/test_pawpal.py::test_three_tasks_in_one_slot_give_one_warning PASSED [ 73%]
tests/test_pawpal.py::test_different_times_do_not_conflict PASSED        [ 76%]
tests/test_pawpal.py::test_same_time_on_different_dates_does_not_conflict PASSED [ 78%]
tests/test_pawpal.py::test_tasks_without_a_time_do_not_conflict PASSED   [ 80%]
tests/test_pawpal.py::test_completed_tasks_are_not_conflicts PASSED      [ 83%]
tests/test_pawpal.py::test_find_conflicts_can_check_a_given_list PASSED  [ 85%]
tests/test_pawpal.py::test_empty_schedule_with_no_pets_or_no_tasks PASSED [ 88%]
tests/test_pawpal.py::test_nothing_fits_in_available_time PASSED         [ 90%]
tests/test_pawpal.py::test_same_priority_shorter_task_goes_first PASSED  [ 92%]
tests/test_pawpal.py::test_sort_by_time_with_unpadded_times PASSED       [ 95%]
tests/test_pawpal.py::test_same_time_typed_differently_still_conflicts PASSED [ 97%]
tests/test_pawpal.py::test_explain_plan_mentions_chosen_and_skipped_tasks PASSED [100%]

============================= 42 passed in 0.06s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Priority: high → low, shorter task first on ties (used to pick tasks). Time: by due date, then `HH:MM`; tasks with no time ("anytime") go last each day (used to display the plan). |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.generate_plan()` | Filter by pet name, completion status, or both. The plan only includes unfinished tasks due today or earlier, and skips tasks that don't fit in the minutes left. |
| Conflict handling | `Scheduler.find_conflicts()` | Warns when 2+ unfinished tasks with a time share the same date **and start time**, for the same pet or different pets. Checks identical start times only, not overlapping durations. Returns warning messages instead of raising errors. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Daily → next copy 1 day later, weekly → 7 days later (using `timedelta`), once → no repeat. Counted from the due date or the completion date, whichever is later. Completing the same task twice doesn't add a duplicate. |

**Sorting.** Priority and time do different jobs. `generate_plan()` uses `sort_by_priority()` to decide which tasks fit in the owner's available minutes. `sort_by_time()` then orders tasks by date and time using `sorted()` with a lambda key. Times are stored as zero-padded 24-hour `HH:MM` text (`"8:05"` becomes `"08:05"`), and an invalid time like `"25:00"` raises a `ValueError` when the task is created, so sorting the text gives the right order.

**Filtering.** `filter_tasks(pet_name=None, completed=None)` returns all tasks, one pet's tasks, done or not-done tasks, or a mix (for example, Luna's unfinished tasks). `None` means "don't filter on this".

**Recurring tasks.** Finish tasks with `pet.complete_task(task)`, not `task.mark_complete()`. `complete_task()` marks the task done and adds its next occurrence to the pet: same details, a new due date, and `completed=False`. Future copies stay out of today's plan until they're due. If a task is finished late, the next copy is counted from the completion date so it isn't already overdue.

**Conflict detection.** `find_conflicts()` groups unfinished tasks that have a time by their (date, time) and returns one message for each slot with 2 or more tasks, like `Conflict at 07:30 on <date>: Morning walk (Mochi), Medicine (Luna)`. Tasks without a time and completed tasks are ignored. **Limitation:** it only compares start times, so a 30-minute task at 07:30 and another task at 07:45 are not flagged even though they overlap. The warnings don't change the plan.

**Streamlit app status:** these four features are in `pawpal_system.py` and shown in `main.py`, but the Streamlit app (`app.py`) doesn't use them yet. It builds the priority-based plan, without task times, recurrence, filters, or conflict warnings.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
