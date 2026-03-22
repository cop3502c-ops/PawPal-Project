from dataclasses import dataclass, field
from typing import List, Tuple, Dict


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

TIME_WINDOWS = {
    "morning":   (8,  12),
    "afternoon": (12, 17),
    "evening":   (17, 22),
}

def format_time(hour: float) -> str:
    """Convert decimal hour (e.g. 13.5) to 12-hour 'H:MM AM/PM' string (e.g. '1:30 PM')."""
    h = int(hour)
    m = int(round((hour - h) * 60))
    if m == 60:
        h += 1
        m = 0
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

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
        """Mark the task as completed."""
        self.completion_flag = True

    def reset_status(self) -> None:
        """Reset the task's completion status to incomplete."""
        self.completion_flag = False

    def fits_in_time_window(self, start_time: float, end_time: float) -> bool:
        """Return True if the task duration fits within the given time window."""
        return self.duration <= (end_time - start_time)


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_notes: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the pet's task list if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def sort_tasks(self, factor: str) -> List[Task]:
        """Return tasks sorted by the given factor: 'priority' or 'category'."""
        if factor == "priority":
            return sorted(self.tasks, key=lambda t: t.priority)
        elif factor == "category":
            return sorted(self.tasks, key=lambda t: t.category)
        return self.tasks


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_time: Tuple[int, int]
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's pet list if it exists."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all tasks across all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

@dataclass
class Scheduler:
    owner: Owner
    tasks: List[Task] = field(default_factory=list)
    constraints: Dict = field(default_factory=dict)

    def sort_tasks_by_priority_and_time(self) -> List[Task]:
        """
        Sorting rules:
          1. Time always comes first: morning → afternoon → evening (top to bottom).
          2. If two tasks share the same time window, order by priority,
             where 1 is the highest priority (lowest number = most urgent).
        """
        tasks = [t for t in self.owner.get_all_tasks() if not t.completion_flag]

        # Rule 1: enforce chronological window order
        time_order = {"morning": 0, "afternoon": 1, "evening": 2}

        # Rule 2: within the same window, lower priority number goes first
        return sorted(
            tasks,
            key=lambda t: (time_order.get(t.preferred_time_of_day, 3), t.priority)
        )

    def fit_tasks_into_schedule(self) -> List[Tuple[str, str, str, str]]:
        """
        Schedule tasks respecting:
          - preferred_time_of_day windows
          - owner's available hours
          - priority order within each window (lower number = more urgent)

        Returns list of (task_title, pet_name, start_str, end_str).
        """
        owner_start, owner_end = self.owner.available_time

        # Each window gets its own cursor so windows don't bleed into each other
        window_cursors: Dict[str, float] = {
            "morning":   max(owner_start, TIME_WINDOWS["morning"][0]),
            "afternoon": max(owner_start, TIME_WINDOWS["afternoon"][0]),
            "evening":   max(owner_start, TIME_WINDOWS["evening"][0]),
            "other":     owner_start,
        }

        schedule = []

        for task in self.sort_tasks_by_priority_and_time():
            pref = task.preferred_time_of_day.lower()
            window = TIME_WINDOWS.get(pref)

            if window:
                win_start, win_end = window
                cursor   = window_cursors[pref]
                start    = max(cursor, win_start)   # never before window opens
                hard_end = min(win_end, owner_end)  # never past window or owner end
            else:
                cursor   = window_cursors["other"]
                start    = cursor
                hard_end = owner_end

            end = start + task.duration

            if end > hard_end:
                print(
                    f"[Scheduler] Skipping '{task.title}' — "
                    f"doesn't fit ({format_time(start)} + {task.duration}h "
                    f"> {format_time(hard_end)})"
                )
                continue

            schedule.append((task.title, task.pet_name, format_time(start), format_time(end)))

            # Advance only this window's cursor
            key = pref if pref in window_cursors else "other"
            window_cursors[key] = end

        # Sort by start time for clean display
        def time_sort_key(entry):
            time_str = entry[2]  # e.g. "8:00 AM"
            period = "PM" in time_str
            parts = time_str.replace("AM", "").replace("PM", "").strip().split(":")
            h, m = int(parts[0]), int(parts[1])
            if period and h != 12:
                h += 12
            if not period and h == 12:
                h = 0
            return h * 60 + m

        schedule.sort(key=time_sort_key)
        return schedule