"""PawPal+ demo script.

Builds a sample owner, pets, and tasks, then prints today's schedule in the
terminal. This shows the logic in pawpal_system.py works without Streamlit.

Run it with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(owner: Owner, plan: list[Task], skipped: list[Task]) -> None:
    """Print the plan as a simple table, then the time left and any skipped tasks."""
    pets = ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets)

    print(f"Today's Schedule for {owner.name}")
    print(f"Pets: {pets}")
    print(f"Time available: {owner.available_minutes} min")
    print("=" * 50)
    print(f"{'#':<4}{'Task':<20}{'Pet':<8}{'Minutes':>8}  Priority")
    print("-" * 50)
    for number, task in enumerate(plan, start=1):
        print(f"{number:<4}{task.title:<20}{task.pet_name:<8}{task.duration_minutes:>8}  {task.priority}")
    print("-" * 50)

    used = sum(task.duration_minutes for task in plan)
    print(f"Time used: {used} min | Time left: {owner.available_minutes - used} min")
    print("Order: highest priority first, shorter tasks first when tied.")

    if skipped:
        print()
        print("Skipped (not enough time left):")
        for task in skipped:
            print(f"  - {task.describe()}")


def main() -> None:
    # The owner has 60 free minutes today.
    owner = Owner("Jordan", available_minutes=60)

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks with a mix of priorities and durations.
    mochi.add_task(Task("Morning walk", 30, "high"))
    mochi.add_task(Task("Breakfast", 10, "high"))
    mochi.add_task(Task("Bath", 40, "medium", frequency="weekly"))
    mochi.add_task(Task("Fetch in the yard", 15, "low"))
    luna.add_task(Task("Breakfast", 5, "high"))
    luna.add_task(Task("Brush fur", 10, "medium"))
    luna.add_task(Task("Laser pointer play", 15, "low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print_schedule(owner, plan, scheduler.skipped_tasks)


if __name__ == "__main__":
    main()
