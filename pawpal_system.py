from dataclasses import dataclass, field
from typing import List, Tuple, Dict


@dataclass
class Task:
    title: str
    category: str
    duration: float
    priority: int
    preferred_time_of_day: str
    pet_name: str  
    completion_flag: bool = False

    def mark_complete(self) -> None:
        self.completion_flag = True

    def reset_status(self) -> None:
        self.completion_flag = False

    def fits_in_time_window(self, start_time, end_time) -> bool:
        return self.duration <= (end_time - start_time)


@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_notes: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

    def sort_tasks(self, factor: str) -> List[Task]:
        if factor == "priority":
            return sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        elif factor == "category":
            return sorted(self.tasks, key=lambda t: t.category)
        return self.tasks


@dataclass
class Owner:
    name: str
    available_time: Tuple[int, int]  
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Scheduler:
    owner: Owner
    tasks: List[Task] = field(default_factory=list)
    constraints: Dict = field(default_factory=dict)

    def sort_tasks_by_priority_and_time(self) -> List[Task]:
        tasks = self.owner.get_all_tasks()

        tasks = [t for t in tasks if not t.completion_flag]

        time_order = {
            "morning": 0,
            "afternoon": 1,
            "evening": 2
        }

        return sorted(
            tasks,
            key=lambda t: (-t.priority, time_order.get(t.preferred_time_of_day, 3))
        )

    def fit_tasks_into_schedule(self):
        start_time, end_time = self.owner.available_time
        current_time = start_time
        schedule = []

        tasks = self.sort_tasks_by_priority_and_time()

        for task in tasks:
            if current_time + task.duration <= end_time:
                schedule.append(
                    (task.title, task.pet_name, current_time, current_time + task.duration)
                )
                current_time += task.duration

        return schedule