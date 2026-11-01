"""Quick tests for the PawPal+ classes in pawpal_system.py."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high"))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Morning walk", 30, "high"))
    assert len(pet.tasks) == 2


def test_high_priority_tasks_come_first():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    # Added lowest priority first, so the scheduler has to reorder them.
    pet.add_task(Task("Play time", 15, "low"))
    pet.add_task(Task("Brush fur", 10, "medium"))
    pet.add_task(Task("Morning walk", 30, "high"))

    plan = Scheduler(owner).generate_plan()

    assert [task.priority for task in plan] == ["high", "medium", "low"]


def test_plan_fits_in_available_time():
    owner = Owner("Jordan", available_minutes=30)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk", 20, "high"))
    pet.add_task(Task("Bath", 40, "medium"))
    pet.add_task(Task("Brush fur", 10, "low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    total = sum(task.duration_minutes for task in plan)
    assert total <= 30
    # Bath is too long for the 10 minutes left after the walk, but Brush fur still fits.
    assert [task.title for task in plan] == ["Morning walk", "Brush fur"]
    assert [task.title for task in scheduler.skipped_tasks] == ["Bath"]


def test_completed_tasks_are_not_scheduled():
    owner = Owner("Jordan", available_minutes=60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    breakfast = Task("Breakfast", 10, "high")
    pet.add_task(breakfast)
    pet.add_task(Task("Morning walk", 30, "high"))

    breakfast.mark_complete()
    plan = Scheduler(owner).generate_plan()

    assert [task.title for task in plan] == ["Morning walk"]


def test_get_all_tasks_collects_from_every_pet():
    owner = Owner("Jordan", available_minutes=60)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Morning walk", 30, "high"))
    mochi.add_task(Task("Breakfast", 10, "high"))
    luna.add_task(Task("Brush fur", 10, "medium"))

    all_tasks = owner.get_all_tasks()

    assert len(all_tasks) == 3
    assert [task.pet_name for task in all_tasks] == ["Mochi", "Mochi", "Luna"]


# --- Sorting by time ---


def test_sort_by_time_orders_earliest_first():
    scheduler = Scheduler(Owner("Jordan", available_minutes=60))
    # Created out of order on purpose.
    tasks = [
        Task("Dinner", 10, "high", time="18:00"),
        Task("Morning walk", 30, "high", time="07:30"),
        Task("Lunch", 10, "high", time="12:15"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.time for task in sorted_tasks] == ["07:30", "12:15", "18:00"]


def test_sort_by_time_puts_anytime_tasks_last():
    scheduler = Scheduler(Owner("Jordan", available_minutes=60))
    tasks = [
        Task("Brush fur", 10, "medium"),  # no time = anytime
        Task("Dinner", 10, "high", time="18:00"),
        Task("Play time", 15, "low"),  # no time = anytime
        Task("Breakfast", 10, "high", time="07:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    # Anytime tasks go last and keep the order they were added in.
    assert [task.title for task in sorted_tasks] == ["Breakfast", "Dinner", "Brush fur", "Play time"]


def test_time_is_normalized_to_hh_mm():
    assert Task("Breakfast", 10, "high", time="8:05").time == "08:05"
    assert Task("Breakfast", 10, "high", time=" 07:30 ").time == "07:30"
    assert Task("Breakfast", 10, "high").time == ""


def test_invalid_time_raises_error():
    for bad_time in ["25:00", "7:30pm", "noon"]:
        with pytest.raises(ValueError):
            Task("Morning walk", 30, "high", time=bad_time)


def test_times_do_not_change_priority_based_plan():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    # The low-priority task is earliest in the day, but priority still decides the plan order.
    pet.add_task(Task("Play time", 15, "low", time="06:00"))
    pet.add_task(Task("Morning walk", 30, "high", time="09:00"))

    plan = Scheduler(owner).generate_plan()

    assert [task.title for task in plan] == ["Morning walk", "Play time"]


# --- Filtering ---


def make_two_pet_owner() -> Owner:
    """Build an owner with Mochi (2 tasks, 1 done) and Luna (2 tasks, 1 done)."""
    owner = Owner("Jordan", available_minutes=60)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high"))
    mochi_breakfast = Task("Breakfast", 10, "high")
    mochi.add_task(mochi_breakfast)
    mochi_breakfast.mark_complete()

    luna.add_task(Task("Brush fur", 10, "medium"))
    luna_breakfast = Task("Breakfast", 5, "high")
    luna.add_task(luna_breakfast)
    luna_breakfast.mark_complete()
    return owner


def test_filter_tasks_by_pet_name():
    scheduler = Scheduler(make_two_pet_owner())

    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")

    assert [task.title for task in mochi_tasks] == ["Morning walk", "Breakfast"]
    assert all(task.pet_name == "Mochi" for task in mochi_tasks)
    assert scheduler.filter_tasks(pet_name="Rex") == []


def test_filter_tasks_by_completion_status():
    scheduler = Scheduler(make_two_pet_owner())

    done = scheduler.filter_tasks(completed=True)
    not_done = scheduler.filter_tasks(completed=False)

    assert [(task.title, task.pet_name) for task in done] == [("Breakfast", "Mochi"), ("Breakfast", "Luna")]
    assert [task.title for task in not_done] == ["Morning walk", "Brush fur"]


def test_filter_tasks_by_pet_and_status():
    scheduler = Scheduler(make_two_pet_owner())

    luna_not_done = scheduler.filter_tasks(pet_name="Luna", completed=False)

    assert [task.title for task in luna_not_done] == ["Brush fur"]


def test_filter_tasks_with_no_filters_returns_everything():
    owner = make_two_pet_owner()

    assert len(Scheduler(owner).filter_tasks()) == len(owner.get_all_tasks()) == 4


# --- Recurring tasks ---
# Most of these use fixed dates (and pass a completed_on date) so they give the same
# result on any day. The few that check today's plan use dates relative to
# date.today() instead, because the plan is always for today.


def test_daily_task_next_occurrence_is_one_day_later():
    task = Task("Breakfast", 10, "high", pet_name="Mochi", frequency="daily",
                time="07:00", due_date=date(2026, 11, 1))
    task.mark_complete()

    next_task = task.next_occurrence(completed_on=date(2026, 11, 1))

    assert next_task.due_date == date(2026, 11, 2)
    assert next_task.completed is False
    # Everything else is copied over.
    assert (next_task.title, next_task.duration_minutes, next_task.priority) == ("Breakfast", 10, "high")
    assert (next_task.pet_name, next_task.frequency, next_task.time) == ("Mochi", "daily", "07:00")


def test_weekly_task_next_occurrence_is_seven_days_later():
    task = Task("Bath", 40, "medium", frequency="weekly", due_date=date(2026, 11, 1))

    assert task.next_occurrence(completed_on=date(2026, 11, 1)).due_date == date(2026, 11, 8)


def test_next_occurrence_crosses_month_and_year():
    daily = Task("Breakfast", 10, "high", frequency="daily", due_date=date(2026, 12, 31))
    weekly = Task("Bath", 40, "medium", frequency="weekly", due_date=date(2026, 12, 28))

    assert daily.next_occurrence(completed_on=date(2026, 12, 31)).due_date == date(2027, 1, 1)
    assert weekly.next_occurrence(completed_on=date(2026, 12, 28)).due_date == date(2027, 1, 4)


def test_once_task_does_not_repeat():
    pet = Pet("Mochi", "dog")
    vet_visit = Task("Vet visit", 45, "high", frequency="once", due_date=date(2026, 11, 1))
    pet.add_task(vet_visit)

    next_task = pet.complete_task(vet_visit)

    assert next_task is None
    assert vet_visit.completed is True
    assert len(pet.tasks) == 1


def test_complete_task_adds_next_occurrence_to_pet():
    pet = Pet("Mochi", "dog")
    breakfast = Task("Breakfast", 10, "high", frequency="daily", due_date=date(2026, 11, 1))
    pet.add_task(breakfast)

    next_task = pet.complete_task(breakfast, completed_on=date(2026, 11, 1))

    assert breakfast.completed is True
    assert len(pet.tasks) == 2
    assert pet.tasks[1] is next_task
    assert next_task.due_date == date(2026, 11, 2)
    assert next_task.pet_name == "Mochi"


def test_completing_a_task_twice_does_not_duplicate():
    pet = Pet("Mochi", "dog")
    breakfast = Task("Breakfast", 10, "high", frequency="daily", due_date=date(2026, 11, 1))
    pet.add_task(breakfast)

    pet.complete_task(breakfast)
    second_result = pet.complete_task(breakfast)

    assert second_result is None
    assert len(pet.tasks) == 2  # the original + one next occurrence, not two


def test_late_completion_counts_from_completion_date():
    pet = Pet("Mochi", "dog")
    breakfast = Task("Breakfast", 10, "high", frequency="daily", due_date=date(2026, 11, 1))
    bath = Task("Bath", 40, "medium", frequency="weekly", due_date=date(2026, 11, 1))
    pet.add_task(breakfast)
    pet.add_task(bath)

    # Both were due Nov 1 but finished 3 days late, on Nov 4.
    next_breakfast = pet.complete_task(breakfast, completed_on=date(2026, 11, 4))
    next_bath = pet.complete_task(bath, completed_on=date(2026, 11, 4))

    assert next_breakfast.due_date == date(2026, 11, 5)  # not Nov 2, which is already past
    assert next_bath.due_date == date(2026, 11, 11)  # not Nov 8


def test_early_completion_keeps_the_schedule():
    pet = Pet("Mochi", "dog")
    breakfast = Task("Breakfast", 10, "high", frequency="daily", due_date=date(2026, 11, 2))
    pet.add_task(breakfast)

    # Finishing Nov 2's breakfast a day early shouldn't create another one due Nov 2.
    next_task = pet.complete_task(breakfast, completed_on=date(2026, 11, 1))

    assert next_task.due_date == date(2026, 11, 3)


def test_late_completed_task_next_copy_is_not_overdue():
    today = date.today()
    owner = Owner("Jordan", available_minutes=60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    missed_walk = Task("Morning walk", 30, "high", due_date=today - timedelta(days=3))
    pet.add_task(missed_walk)

    next_walk = pet.complete_task(missed_walk)  # completed today

    assert next_walk.due_date == today + timedelta(days=1)
    assert Scheduler(owner).generate_plan() == []  # nothing overdue left for today


def test_frequency_is_checked():
    assert Task("Bath", 40, "medium", frequency="Weekly").frequency == "weekly"
    with pytest.raises(ValueError):
        Task("Bath", 40, "medium", frequency="monthly")


def test_future_tasks_are_not_in_todays_plan():
    # These dates are relative to today, since the plan is always for today.
    today = date.today()
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk", 30, "high", due_date=today))
    pet.add_task(Task("Bath", 40, "medium", due_date=today + timedelta(days=1)))
    pet.add_task(Task("Missed brushing", 10, "low", due_date=today - timedelta(days=1)))

    plan = Scheduler(owner).generate_plan()

    # Tomorrow's task waits; yesterday's missed task still shows up.
    assert [task.title for task in plan] == ["Morning walk", "Missed brushing"]


def test_completed_daily_task_next_copy_waits_for_tomorrow():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    breakfast = Task("Breakfast", 10, "high")  # due today by default
    pet.add_task(breakfast)
    pet.add_task(Task("Morning walk", 30, "high"))

    pet.complete_task(breakfast)
    plan = Scheduler(owner).generate_plan()

    assert [task.title for task in plan] == ["Morning walk"]
    assert len(pet.tasks) == 3  # tomorrow's Breakfast exists, it's just not in today's plan


def test_sort_by_time_puts_earlier_days_first():
    scheduler = Scheduler(Owner("Jordan", available_minutes=60))
    tomorrow_breakfast = Task("Breakfast", 10, "high", time="07:00", due_date=date(2026, 11, 2))
    today_walk = Task("Morning walk", 30, "high", time="09:00", due_date=date(2026, 11, 1))

    sorted_tasks = scheduler.sort_by_time([tomorrow_breakfast, today_walk])

    assert [task.title for task in sorted_tasks] == ["Morning walk", "Breakfast"]


# --- Conflict detection ---
# Fixed dates are fine here because find_conflicts doesn't depend on today's date.

DAY_ONE = date(2026, 11, 1)
DAY_TWO = date(2026, 11, 2)


def make_mochi_and_luna() -> tuple[Owner, Pet, Pet]:
    """Build an owner with two pets and no tasks yet."""
    owner = Owner("Jordan", available_minutes=60)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner, mochi, luna


def test_two_tasks_at_same_time_conflict():
    owner, mochi, luna = make_mochi_and_luna()
    mochi.add_task(Task("Morning walk", 30, "high", time="08:00", due_date=DAY_ONE))
    mochi.add_task(Task("Breakfast", 10, "high", time="08:00", due_date=DAY_ONE))

    warnings = Scheduler(owner).find_conflicts()

    assert warnings == ["Conflict at 08:00 on 2026-11-01: Morning walk (Mochi), Breakfast (Mochi)"]


def test_conflict_between_different_pets():
    owner, mochi, luna = make_mochi_and_luna()
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30", due_date=DAY_ONE))
    luna.add_task(Task("Medicine", 5, "high", time="07:30", due_date=DAY_ONE))

    warnings = Scheduler(owner).find_conflicts()

    assert len(warnings) == 1
    assert "07:30" in warnings[0]
    assert "Morning walk (Mochi)" in warnings[0]
    assert "Medicine (Luna)" in warnings[0]


def test_three_tasks_in_one_slot_give_one_warning():
    owner, mochi, luna = make_mochi_and_luna()
    mochi.add_task(Task("Morning walk", 30, "high", time="08:00", due_date=DAY_ONE))
    mochi.add_task(Task("Breakfast", 10, "high", time="08:00", due_date=DAY_ONE))
    luna.add_task(Task("Breakfast", 5, "high", time="08:00", due_date=DAY_ONE))

    warnings = Scheduler(owner).find_conflicts()

    assert warnings == [
        "Conflict at 08:00 on 2026-11-01: Morning walk (Mochi), Breakfast (Mochi), Breakfast (Luna)"
    ]


def test_different_times_do_not_conflict():
    owner, mochi, luna = make_mochi_and_luna()
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30", due_date=DAY_ONE))
    luna.add_task(Task("Medicine", 5, "high", time="07:45", due_date=DAY_ONE))

    assert Scheduler(owner).find_conflicts() == []


def test_same_time_on_different_dates_does_not_conflict():
    owner, mochi, luna = make_mochi_and_luna()
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30", due_date=DAY_ONE))
    luna.add_task(Task("Grooming", 20, "low", time="07:30", due_date=DAY_TWO))

    assert Scheduler(owner).find_conflicts() == []


def test_tasks_without_a_time_do_not_conflict():
    owner, mochi, luna = make_mochi_and_luna()
    mochi.add_task(Task("Brush fur", 10, "medium", due_date=DAY_ONE))  # anytime
    luna.add_task(Task("Play time", 15, "low", due_date=DAY_ONE))  # anytime

    assert Scheduler(owner).find_conflicts() == []


def test_completed_tasks_are_not_conflicts():
    owner, mochi, luna = make_mochi_and_luna()
    breakfast = Task("Breakfast", 10, "high", time="08:00", due_date=DAY_ONE)
    mochi.add_task(breakfast)
    luna.add_task(Task("Breakfast", 5, "high", time="08:00", due_date=DAY_ONE))

    breakfast.mark_complete()

    assert Scheduler(owner).find_conflicts() == []


def test_find_conflicts_can_check_a_given_list():
    owner, mochi, luna = make_mochi_and_luna()
    walk = Task("Morning walk", 30, "high", time="07:30", due_date=DAY_ONE)
    medicine = Task("Medicine", 5, "high", time="07:30", due_date=DAY_ONE)
    training = Task("Training", 15, "medium", time="07:45", due_date=DAY_ONE)
    mochi.add_task(walk)
    luna.add_task(medicine)
    mochi.add_task(training)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts([walk, training]) == []
    assert len(scheduler.find_conflicts([walk, medicine])) == 1


# --- Edge cases ---
# These use the default due date (today) instead of fixed dates, so they never go stale.


def test_empty_schedule_with_no_pets_or_no_tasks():
    owner_with_no_pets = Owner("Jordan", available_minutes=60)
    owner_with_empty_pet = Owner("Sam", available_minutes=60)
    owner_with_empty_pet.add_pet(Pet("Mochi", "dog"))  # a pet with no tasks yet

    for owner in [owner_with_no_pets, owner_with_empty_pet]:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()

        assert owner.get_all_tasks() == []
        assert plan == []
        assert scheduler.skipped_tasks == []
        assert scheduler.find_conflicts() == []
        assert scheduler.explain_plan(plan) == "No tasks to schedule."


def test_nothing_fits_in_available_time():
    owner = Owner("Jordan", available_minutes=5)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    # Added lowest priority first, so the skipped list has to be sorted.
    pet.add_task(Task("Bath", 30, "low"))
    pet.add_task(Task("Morning walk", 10, "high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    explanation = scheduler.explain_plan(plan)

    assert plan == []
    # Every task is skipped, highest priority first.
    assert [task.title for task in scheduler.skipped_tasks] == ["Morning walk", "Bath"]
    assert "No tasks fit in the available time." in explanation
    assert "Total: 0 of 5 minutes used." in explanation


def test_same_priority_shorter_task_goes_first():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk", 30, "high"))
    pet.add_task(Task("Treat", 1, "medium"))  # shortest overall, but lower priority
    pet.add_task(Task("Medicine", 5, "high"))
    pet.add_task(Task("Breakfast", 10, "high"))

    plan = Scheduler(owner).generate_plan()

    # High-priority tasks go shortest first; duration only breaks ties, so Treat is still last.
    assert [task.title for task in plan] == ["Medicine", "Breakfast", "Morning walk", "Treat"]


def test_sort_by_time_with_unpadded_times():
    scheduler = Scheduler(Owner("Jordan", available_minutes=60))
    tasks = [
        Task("Lunch", 10, "high", time="10:00"),
        Task("Morning walk", 30, "high", time="9:00"),
        Task("Breakfast", 10, "high", time="8:30"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    # As plain text, "10:00" would sort before "9:00". Stored as "09:00", it sorts correctly.
    assert [task.title for task in sorted_tasks] == ["Breakfast", "Morning walk", "Lunch"]
    assert [task.time for task in sorted_tasks] == ["08:30", "09:00", "10:00"]


def test_same_time_typed_differently_still_conflicts():
    owner, mochi, luna = make_mochi_and_luna()
    walk = Task("Morning walk", 30, "high", time="8:00")
    breakfast = Task("Breakfast", 5, "high", time="08:00")
    mochi.add_task(walk)
    luna.add_task(breakfast)

    warnings = Scheduler(owner).find_conflicts()

    assert warnings == [f"Conflict at 08:00 on {walk.due_date}: Morning walk (Mochi), Breakfast (Luna)"]


def test_explain_plan_mentions_chosen_and_skipped_tasks():
    owner = Owner("Jordan", available_minutes=40)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk", 30, "high"))
    pet.add_task(Task("Breakfast", 10, "high"))
    pet.add_task(Task("Bath", 40, "medium"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    explanation = scheduler.explain_plan(plan)

    assert "Daily plan for Jordan (40 minutes available):" in explanation
    assert "1. Breakfast (Mochi) - 10 min, high priority" in explanation
    assert "2. Morning walk (Mochi) - 30 min, high priority" in explanation
    assert "Total: 40 of 40 minutes used." in explanation
    assert "Skipped because there wasn't enough time left:" in explanation
    assert "- Bath (Mochi) - 40 min, medium priority" in explanation
    assert "3." not in explanation  # Bath is only listed as skipped, not as part of the plan
