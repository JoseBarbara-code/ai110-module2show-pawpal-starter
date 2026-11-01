"""PawPal+ system classes.

Based on diagrams/uml_draft.mmd. An Owner has Pets, each Pet has Tasks,
and the Scheduler builds a daily plan from the owner's tasks and available time.
"""

from dataclasses import dataclass, field

# Higher number = more important. Used to sort tasks.
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or grooming."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    pet_name: str = ""  # filled in by Pet.add_task so the plan shows whose task it is
    frequency: str = "daily"  # "daily" or "weekly"
    completed: bool = False

    def priority_rank(self) -> int:
        """Return a number for the priority so tasks can be sorted."""
        # Unknown priorities (like a typo) get 0 so they go to the end of the list.
        return PRIORITY_RANKS.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

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

    def generate_plan(self) -> list[Task]:
        """Choose and order tasks that fit in the owner's available time."""
        # Completed tasks are already done, so they don't need a spot in today's plan.
        to_do = [task for task in self.owner.get_all_tasks() if not task.completed]

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
