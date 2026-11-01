"""PawPal+ system classes.

Class skeletons based on diagrams/uml_draft.mmd.
The method bodies are placeholders; the logic will be added in a later step.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or grooming."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    pet_name: str = ""  # filled in by Pet.add_task so the plan shows whose task it is

    def priority_rank(self) -> int:
        """Return a number for the priority so tasks can be sorted."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and set the task's pet_name."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        pass


class Owner:
    """A pet owner, their pets, and how much time they have each day."""

    def __init__(self, name: str, available_minutes: int, preferences: list[str] | None = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences if preferences is not None else []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks from all of this owner's pets in one list."""
        pass


class Scheduler:
    """Builds a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> list[Task]:
        """Choose and order tasks that fit in the owner's available time."""
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a short explanation of why each task was chosen."""
        pass
