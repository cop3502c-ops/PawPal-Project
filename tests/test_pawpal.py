import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Task, Pet


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