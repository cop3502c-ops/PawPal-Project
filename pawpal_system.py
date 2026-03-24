from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from datetime import date, timedelta


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
    frequency: str = "once"          # "once" | "daily" | "weekly"
    due_date: Optional[date] = None  # tracks when this occurrence is due

    def mark_complete(self) -> Optional["Task"]:
        """
        Mark the task as completed.
        If frequency is 'daily' or 'weekly', automatically creates and returns
        a new Task instance for the next occurrence using timedelta.
        Returns None if frequency is 'once'.
        """
        self.completion_flag = True

        if self.frequency == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
            return Task(
                title=self.title,
                category=self.category,
                duration=self.duration,
                priority=self.priority,
                preferred_time_of_day=self.preferred_time_of_day,
                pet_name=self.pet_name,
                frequency=self.frequency,
                due_date=next_due,
            )
        elif self.frequency == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(weeks=1)
            return Task(
                title=self.title,
                category=self.category,
                duration=self.duration,
                priority=self.priority,
                preferred_time_of_day=self.preferred_time_of_day,
                pet_name=self.pet_name,
                frequency=self.frequency,
                due_date=next_due,
            )

        return None  # "once" tasks don't recur

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

    def complete_task(self, task: Task) -> None:
        """
        Mark a task complete and, if it recurs, auto-add the next occurrence.
        Uses timedelta internally via task.mark_complete().
        """
        next_task = task.mark_complete()
        if next_task:
            self.tasks.append(next_task)

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
        time_order = {"morning": 0, "afternoon": 1, "evening": 2}
        return sorted(
            tasks,
            key=lambda t: (time_order.get(t.preferred_time_of_day, 3), t.priority)
        )

    def sort_by_time(self) -> List[Task]:
        """
        Sort all tasks by time window only: morning → afternoon → evening.
        Uses a lambda key on preferred_time_of_day string.
        """
        time_order = {"morning": 0, "afternoon": 1, "evening": 2}
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda t: time_order.get(t.preferred_time_of_day, 3)
        )

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> List[Task]:
        """
        Filter tasks by completion status and/or pet name.
          - completed=True  → only completed tasks
          - completed=False → only incomplete tasks
          - completed=None  → all tasks regardless of status
          - pet_name        → only tasks belonging to that pet (case-insensitive)
        """
        tasks = self.owner.get_all_tasks()

        if completed is not None:
            tasks = [t for t in tasks if t.completion_flag == completed]

        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]

        return tasks

    def detect_conflicts(self, schedule: List[Tuple[str, str, str, str]]) -> List[str]:
        """
        Lightweight conflict detection — checks if any two scheduled tasks
        overlap in time. Returns a list of warning strings rather than crashing.

        Two tasks conflict if one starts before the other ends:
            A.start < B.end AND B.start < A.end
        """
        warnings = []

        def to_minutes(time_str: str) -> int:
            period = "PM" in time_str
            parts = time_str.replace("AM", "").replace("PM", "").strip().split(":")
            h, m = int(parts[0]), int(parts[1])
            if period and h != 12:
                h += 12
            if not period and h == 12:
                h = 0
            return h * 60 + m

        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                title_a, pet_a, start_a, end_a = schedule[i]
                title_b, pet_b, start_b, end_b = schedule[j]

                a_start = to_minutes(start_a)
                a_end   = to_minutes(end_a)
                b_start = to_minutes(start_b)
                b_end   = to_minutes(end_b)

                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"⚠️  Conflict: '{title_a}' ({pet_a}) [{start_a}–{end_a}] "
                        f"overlaps with '{title_b}' ({pet_b}) [{start_b}–{end_b}]"
                    )

        return warnings

    def fit_tasks_into_schedule(self) -> List[Tuple[str, str, str, str]]:
        """
        Scheduling rules:
          1. Time window comes first: morning (8-12) → afternoon (12-17) → evening (17-22).
             A task never leaves its assigned window regardless of priority.
          2. Within the same window, lower priority number is scheduled first (1 = most urgent).
          3. Each pet has its own cursor per window — pets run in parallel.
             This means two pets can have overlapping tasks, which detect_conflicts() will catch.
          4. A task is skipped if its duration doesn't fit in the remaining window time
             or would exceed the owner's available hours.

        Returns list of (task_title, pet_name, start_str, end_str).
        """
        owner_start, owner_end = self.owner.available_time

        # Per-pet, per-window cursors so pets run in parallel
        # Structure: pet_cursors[pet_name][window] = current_time
        pet_cursors: Dict[str, Dict[str, float]] = {}
        for pet in self.owner.pets:
            pet_cursors[pet.name] = {
                "morning":   max(owner_start, TIME_WINDOWS["morning"][0]),
                "afternoon": max(owner_start, TIME_WINDOWS["afternoon"][0]),
                "evening":   max(owner_start, TIME_WINDOWS["evening"][0]),
                "other":     owner_start,
            }

        schedule = []

        for task in self.sort_tasks_by_priority_and_time():
            pref = task.preferred_time_of_day.lower()
            window = TIME_WINDOWS.get(pref)
            cursors = pet_cursors.get(task.pet_name, {})

            if window:
                win_start, win_end = window
                cursor   = cursors.get(pref, max(owner_start, win_start))
                start    = max(cursor, win_start)
                hard_end = min(win_end, owner_end)
            else:
                cursor   = cursors.get("other", owner_start)
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

            # Advance only this pet's cursor for this window
            key = pref if pref in cursors else "other"
            pet_cursors[task.pet_name][key] = end

        def time_sort_key(entry):
            time_str = entry[2]
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