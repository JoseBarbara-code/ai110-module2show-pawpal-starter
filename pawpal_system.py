"""PawPal+ system classes.

Based on diagrams/uml_draft.mmd. An Owner has Pets, each Pet has Tasks,
and the Scheduler builds a daily plan from the owner's tasks and available time.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

# Higher number = more important. Used to sort tasks.
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}

# How often a task repeats. "once" tasks don't repeat.
FREQUENCIES = ["daily", "weekly", "once"]


def normalize_time(time_text: str) -> str:
    """Return a time as 24-hour 'HH:MM' (so '8:05' becomes '08:05'); '' means anytime."""
    time_text = time_text.strip()
    if time_text == "":
        return ""
    try:
        parsed = datetime.strptime(time_text, "%H:%M")
    except ValueError:
        raise ValueError(
            f"Time must be 24-hour HH:MM, like '08:00' or '14:30' (got {time_text!r})."
        )
    return parsed.strftime("%H:%M")


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or grooming."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    pet_name: str = ""  # filled in by Pet.add_task so the plan shows whose task it is
    frequency: str = "daily"  # "daily", "weekly", or "once"
    completed: bool = False
    time: str = ""  # scheduled time as 24-hour "HH:MM"; "" means anytime
    due_date: date = field(default_factory=date.today)  # the day this task is due

    def __post_init__(self) -> None:
        """Check the time and frequency when the task is created."""
        # Zero-padded times like "08:00" sort correctly as text; "8:00" would not.
        self.time = normalize_time(self.time)

        self.frequency = self.frequency.strip().lower()
        if self.frequency not in FREQUENCIES:
            raise ValueError(
                f"Frequency must be 'daily', 'weekly', or 'once' (got {self.frequency!r})."
            )

    def priority_rank(self) -> int:
        """Return a number for the priority so tasks can be sorted."""
        # Unknown priorities (like a typo) get 0 so they go to the end of the list.
        return PRIORITY_RANKS.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as done (use Pet.complete_task() so repeating tasks get their next copy)."""
        self.completed = True

    def edit(self, title: str, duration_minutes: int, priority: str, time: str,
             due_date: date, frequency: str) -> None:
        """Change this task's details, keeping its pet and completion status (ValueError if invalid)."""
        # Build a temporary Task first so the usual time and frequency checks run.
        # If anything is invalid, ValueError is raised and this task stays unchanged.
        checked = Task(title, duration_minutes, priority, frequency=frequency,
                       time=time, due_date=due_date)
        self.title = checked.title
        self.duration_minutes = checked.duration_minutes
        self.priority = checked.priority
        self.frequency = checked.frequency
        self.time = checked.time
        self.due_date = checked.due_date

    def next_occurrence(self, completed_on: date | None = None) -> "Task | None":
        """Return a new, not-done copy of this task for its next due date (None for 'once' tasks)."""
        if completed_on is None:
            completed_on = date.today()
        # Count from the due date or the day it was completed, whichever is later.
        # On time or early, the schedule stays the same; late, it starts again from the completion day.
        start_date = max(self.due_date, completed_on)

        if self.frequency == "daily":
            next_due_date = start_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due_date = start_date + timedelta(days=7)
        else:
            return None  # "once" tasks don't repeat

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_name=self.pet_name,
            frequency=self.frequency,
            completed=False,
            time=self.time,
            due_date=next_due_date,
        )

    def describe(self) -> str:
        """Return a short one-line description, like 'Walk (Mochi) - 30 min, high priority'."""
        pet = f" ({self.pet_name})" if self.pet_name else ""
        return f"{self.title}{pet} - {self.duration_minutes} min, {self.priority} priority"


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and set the task's pet_name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first task with the given title (does nothing if there isn't one)."""
        for task in self.tasks:
            if task.title == title:
                self.tasks.remove(task)
                return

    def complete_task(self, task: Task, completed_on: date | None = None) -> Task | None:
        """Mark a task done and add its next occurrence; return the new task (or None)."""
        # Always finish tasks through this method, not Task.mark_complete() directly.
        # Calling mark_complete() alone skips the next occurrence, and afterwards this
        # method sees the task as already done and won't add one either.
        if task.completed:
            # Already done, so its next occurrence was already added. Don't add another.
            return None

        task.mark_complete()
        next_task = task.next_occurrence(completed_on)
        if next_task is not None:
            self.add_task(next_task)
        return next_task


class Owner:
    """A pet owner, their pets, and how much time they have each day."""

    def __init__(self, name: str, available_minutes: int, preferences: list[str] | None = None):
        """Create an owner with a name, free minutes for today, and optional preferences."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences if preferences is not None else []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks from all of this owner's pets in one list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """Builds a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that plans tasks for the given owner."""
        self.owner = owner
        self.skipped_tasks: list[Task] = []  # filled in by generate_plan

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks from highest to lowest priority, shorter tasks first when tied."""
        return sorted(tasks, key=lambda task: (-task.priority_rank(), task.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks from earliest to latest (by date, then time), with anytime tasks last each day."""
        # (task.time == "") is False for timed tasks and True for anytime tasks.
        # False sorts before True, so anytime tasks end up at the end of their day.
        return sorted(tasks, key=lambda task: (task.due_date, task.time == "", task.time))

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Return the owner's tasks for one pet, one completion status, or both (None means any)."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet_name == pet_name]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        return tasks

    def find_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return a warning for each date and time that has 2 or more tasks (empty list if none)."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        # Group tasks by their (date, time) slot. Sorting first keeps the warnings in order.
        tasks_by_slot = {}
        for task in self.sort_by_time(tasks):
            if task.completed or task.time == "":
                continue  # done tasks and anytime tasks can't clash with anything
            slot = (task.due_date, task.time)
            if slot not in tasks_by_slot:
                tasks_by_slot[slot] = []
            tasks_by_slot[slot].append(task)

        # Any slot holding more than one task is a conflict.
        warnings = []
        for (due_date, time), slot_tasks in tasks_by_slot.items():
            if len(slot_tasks) > 1:
                names = ", ".join(f"{task.title} ({task.pet_name or 'no pet'})" for task in slot_tasks)
                warnings.append(f"Conflict at {time} on {due_date}: {names}")
        return warnings

    def generate_plan(self) -> list[Task]:
        """Choose and order tasks that fit in the owner's available time."""
        # Only plan tasks that aren't done yet and are due today or earlier.
        # Future tasks (like tomorrow's copy of a daily task) wait for their own day,
        # while a missed task from an earlier day still shows up.
        today = date.today()
        to_do = [task for task in self.filter_tasks(completed=False) if task.due_date <= today]

        plan = []
        self.skipped_tasks = []
        time_left = self.owner.available_minutes

        for task in self.sort_by_priority(to_do):
            if task.duration_minutes <= time_left:
                plan.append(task)
                time_left -= task.duration_minutes
            else:
                # Keep going: a shorter task further down the list might still fit.
                self.skipped_tasks.append(task)

        return plan

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a short explanation of why each task was chosen."""
        if not plan and not self.skipped_tasks:
            return "No tasks to schedule."

        available = self.owner.available_minutes
        used = sum(task.duration_minutes for task in plan)

        lines = [
            f"Daily plan for {self.owner.name} ({available} minutes available):",
            "Tasks are picked from highest to lowest priority (shorter tasks first when tied), "
            "as long as they fit in the time left.",
        ]
        if plan:
            for number, task in enumerate(plan, start=1):
                lines.append(f"  {number}. {task.describe()}")
        else:
            lines.append("  No tasks fit in the available time.")
        lines.append(f"Total: {used} of {available} minutes used.")

        if self.skipped_tasks:
            lines.append("Skipped because there wasn't enough time left:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.describe()}")

        return "\n".join(lines)
