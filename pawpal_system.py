from dataclasses import dataclass, field
from typing import List, Tuple, Dict


# ----------------------
# Task
# ----------------------
@dataclass
class Task:
    title: str
    category: str
    duration: float
    priority: int
    preferred_time_of_day: str
    pet_name: str  #  FIX 1: Added reference to which pet this task belongs to
    completion_flag: bool = False

    def mark_complete(self) -> None:
        pass

    def reset_status(self) -> None:
        pass

    def fits_in_time_window(self, start_time, end_time) -> bool:
        pass


# ----------------------
# Pet
# ----------------------
@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_notes: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def sort_tasks(self, factor: str) -> List[Task]:
        pass


# ----------------------
# Owner
# ----------------------
@dataclass
class Owner:
    name: str
    available_time: Tuple[int, int]  # FIX 2: Made time explicit (start_hour, end_hour as ints)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


# ----------------------
# Scheduler
# ----------------------
@dataclass
class Scheduler:
    owner: Owner
    tasks: List[Task] = field(default_factory=list)
    constraints: Dict = field(default_factory=dict)

    def sort_tasks_by_priority_and_time(self) -> List[Task]:
        pass

    def fit_tasks_into_schedule(self):
        pass