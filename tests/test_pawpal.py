import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion():
    task = Task(
        title="Morning Walk",
        category="Exercise",
        duration=1,
        priority=3,
        preferred_time_of_day="morning",
        pet_name="Buddy"
    )
    task.mark_complete()
    assert task.completion_flag == True


def test_task_addition():
    pet = Pet(name="Buddy", species="Dog", age=5, care_notes="Needs daily walks")
    task = Task(
        title="Evening Play",
        category="Enrichment",
        duration=1,
        priority=1,
        preferred_time_of_day="evening",
        pet_name="Buddy"
    )
    pet.add_task(task)
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting Correctness
# ---------------------------------------------------------------------------

def test_sorting_chronological_order():
    """Tasks should be returned morning -> afternoon -> evening regardless of add order."""
    owner = Owner(name="Alex", available_time=(8, 22))
    pet = Pet(name="Buddy", species="Dog", age=3, care_notes="")

    pet.add_task(Task("Evening Play",  "Enrichment", 1, 1, "evening",   "Buddy"))
    pet.add_task(Task("Afternoon Nap", "Rest",       1, 1, "afternoon", "Buddy"))
    pet.add_task(Task("Morning Walk",  "Exercise",   1, 1, "morning",   "Buddy"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    sorted_tasks = scheduler.sort_tasks_by_priority_and_time()
    windows = [t.preferred_time_of_day for t in sorted_tasks]

    assert windows == ["morning", "afternoon", "evening"], \
        f"Expected chronological order, got {windows}"


# ---------------------------------------------------------------------------
# Recurrence Logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_task():
    """Marking a daily task complete should create a new task due tomorrow."""
    today = date.today()
    pet = Pet(name="Buddy", species="Dog", age=3, care_notes="")
    task = Task(
        title="Morning Walk",
        category="Exercise",
        duration=1,
        priority=1,
        preferred_time_of_day="morning",
        pet_name="Buddy",
        frequency="daily",
        due_date=today
    )
    pet.add_task(task)
    pet.complete_task(task)

    # Should now have 2 tasks: original (complete) + next occurrence
    assert len(pet.tasks) == 2, f"Expected 2 tasks, got {len(pet.tasks)}"

    next_task = pet.tasks[1]
    assert next_task.completion_flag == False, "Next task should not be complete"
    assert next_task.due_date == today + timedelta(days=1), \
        f"Expected due date {today + timedelta(days=1)}, got {next_task.due_date}"


# ---------------------------------------------------------------------------
# Conflict Detection
# ---------------------------------------------------------------------------

def test_conflict_detection_flags_overlap():
    """Two pets with tasks in the same window should trigger a conflict warning."""
    owner = Owner(name="Alex", available_time=(8, 22))

    dog = Pet(name="Buddy",    species="Dog", age=5, care_notes="")
    cat = Pet(name="Whiskers", species="Cat", age=3, care_notes="")

    dog.add_task(Task("Morning Walk", "Exercise", 2, 1, "morning", "Buddy"))
    cat.add_task(Task("Feed Cat",     "Feeding",  2, 1, "morning", "Whiskers"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner=owner)
    schedule  = scheduler.fit_tasks_into_schedule()
    conflicts = scheduler.detect_conflicts(schedule)

    assert len(conflicts) > 0, "Expected at least one conflict warning, got none"
    #python -m pytest"