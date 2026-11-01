"""PawPal+ demo script.

Builds a sample owner, pets, and tasks, then prints today's schedule in the
terminal. This shows the logic in pawpal_system.py works without Streamlit.

Run it with:  python main.py
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(owner: Owner, plan: list[Task], skipped: list[Task]) -> None:
    """Print the plan as a simple table, then the time left and any skipped tasks."""
    pets = ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets)

    print(f"Today's Schedule for {owner.name}")
    print(f"Pets: {pets}")
    print(f"Time available: {owner.available_minutes} min")
    print("=" * 56)
    print(f"{'Time':<9}{'Task':<20}{'Pet':<8}{'Minutes':>8}  Priority")
    print("-" * 56)
    for task in plan:
        time = task.time or "anytime"
        print(f"{time:<9}{task.title:<20}{task.pet_name:<8}{task.duration_minutes:>8}  {task.priority}")
    print("-" * 56)

    used = sum(task.duration_minutes for task in plan)
    print(f"Time used: {used} min | Time left: {owner.available_minutes - used} min")
    print("Tasks are chosen by priority to fit your time, then listed by time of day.")

    if skipped:
        print()
        print("Skipped (not enough time left):")
        for task in skipped:
            print(f"  - {task.describe()}")


def print_task_list(heading: str, tasks: list[Task]) -> None:
    """Print a heading and one line per task, with its time, due date (if not today), and status."""
    print()
    print(heading)
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        time = task.time or "anytime"
        due = f" (due {task.due_date})" if task.due_date != date.today() else ""
        done = " [done]" if task.completed else ""
        print(f"  {time:<9}{task.describe()}{due}{done}")


def print_conflicts(heading: str, warnings: list[str]) -> None:
    """Print a heading and each conflict warning, or say there are none."""
    print(f"  {heading}")
    if not warnings:
        print("    No conflicts.")
    for warning in warnings:
        print(f"    WARNING: {warning}")


def main() -> None:
    # The owner has 60 free minutes today.
    owner = Owner("Jordan", available_minutes=60)

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added out of time order on purpose, so sorting has work to do.
    # Tasks without a time are "anytime" tasks.
    morning_walk = Task("Morning walk", 30, "high", time="07:30")
    mochi.add_task(morning_walk)
    bath = Task("Bath", 40, "medium", frequency="weekly")
    mochi.add_task(bath)
    mochi_breakfast = Task("Breakfast", 10, "high", time="07:00")
    mochi.add_task(mochi_breakfast)
    mochi.add_task(Task("Fetch in the yard", 15, "low", time="17:00"))
    luna.add_task(Task("Laser pointer play", 15, "low", time="19:00"))
    luna.add_task(Task("Brush fur", 10, "medium"))
    luna.add_task(Task("Breakfast", 5, "high", time="8:00"))  # stored as "08:00"

    # One task is already done today, so it shouldn't be scheduled again.
    litter_box = Task("Litter box", 5, "high", time="07:15")
    luna.add_task(litter_box)
    litter_box.mark_complete()

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    # Priority picks the tasks; sort_by_time puts them in time-of-day order.
    print_schedule(owner, scheduler.sort_by_time(plan), scheduler.skipped_tasks)

    # --- Sorting and filtering demos ---
    print_task_list("All tasks sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))
    print_task_list(
        "Filter - Mochi's tasks:", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi"))
    )
    print_task_list("Filter - completed tasks:", scheduler.filter_tasks(completed=True))
    print_task_list(
        "Filter - Luna's tasks that aren't done:",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna", completed=False)),
    )

    # A badly formatted time is rejected instead of being sorted in the wrong place.
    print()
    try:
        Task("Nap", 20, "low", time="25:00")
    except ValueError as error:
        print(f"Invalid time rejected: {error}")

    # --- Recurring tasks ---
    print()
    print("Recurring tasks:")
    vet_visit = Task("Vet visit", 45, "high", frequency="once", time="10:00")
    mochi.add_task(vet_visit)

    # complete_task marks the task done and adds its next occurrence to the pet.
    for task in [mochi_breakfast, bath, vet_visit]:
        next_task = mochi.complete_task(task)
        if next_task is None:
            print(f"  Completed {task.title} ({task.frequency}) -> doesn't repeat")
        else:
            print(
                f"  Completed {task.title} ({task.frequency}, due {task.due_date})"
                f" -> next one due {next_task.due_date}"
            )

    # Completing the same task again doesn't add another copy.
    count_before = len(mochi.tasks)
    mochi.complete_task(mochi_breakfast)
    print(f"  Completed Breakfast again -> Mochi still has {len(mochi.tasks)} tasks (was {count_before})")

    # Tomorrow's Breakfast and next week's Bath aren't due yet, so they stay out of today's plan.
    plan = scheduler.generate_plan()
    print_task_list("Today's plan after completing those tasks:", scheduler.sort_by_time(plan))
    print_task_list(
        "Mochi's tasks that aren't done (including future ones):",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)),
    )

    # --- Conflict detection ---
    print()
    print("Conflict check:")
    print_conflicts("Current tasks:", scheduler.find_conflicts())

    # Luna's medicine is at the same time as Mochi's walk, so that's a real conflict.
    medicine = Task("Medicine", 5, "high", time="07:30")
    luna.add_task(medicine)
    # These two should NOT be flagged: a different time, and the same time on a different day.
    training = Task("Training", 15, "medium", time="07:45")
    mochi.add_task(training)
    grooming = Task("Grooming", 20, "low", time="07:30", frequency="once",
                    due_date=date.today() + timedelta(days=1))
    luna.add_task(grooming)

    print_conflicts(
        "After adding Medicine (07:30), Training (07:45), and Grooming (07:30 tomorrow):",
        scheduler.find_conflicts(),
    )
    print_conflicts(
        "Different times - Morning walk 07:30 vs Training 07:45:",
        scheduler.find_conflicts([morning_walk, training]),
    )
    print_conflicts(
        "Different dates - Medicine 07:30 today vs Grooming 07:30 tomorrow:",
        scheduler.find_conflicts([medicine, grooming]),
    )


if __name__ == "__main__":
    main()
