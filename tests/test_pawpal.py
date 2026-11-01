"""Quick tests for the PawPal+ classes in pawpal_system.py."""

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
