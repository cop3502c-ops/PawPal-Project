from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date


def main():
    # Create owner
    owner = Owner(name="Alex", available_time=(8, 22))  # 8 AM to 10 PM

    # Create pets
    dog = Pet(name="Buddy", species="Dog", age=5, care_notes="Needs daily walks")
    cat = Pet(name="Whiskers", species="Cat", age=3, care_notes="Loves quiet time")

    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks
    # Time always comes first, from morning in top to evening in bottom
    # If 2 tasks have the same time, they are ordered by priority, with 1 being the highest priority
    task1 = Task(
        title="Morning Walk",
        category="Exercise",
        duration=1,
        priority=1,
        preferred_time_of_day="morning",
        pet_name="Buddy",
        frequency="daily",
        due_date=date.today()
    )

    task2 = Task(
        title="Feed Cat",
        category="Feeding",
        duration=2,
        priority=1,
        preferred_time_of_day="morning",
        pet_name="Whiskers",
        frequency="daily",
        due_date=date.today()
    )

    task3 = Task(
        title="Evening Play",
        category="Enrichment",
        duration=2,
        priority=3,
        preferred_time_of_day="evening",
        pet_name="Buddy",
        frequency="weekly",
        due_date=date.today()
    )

    # Conflict test: same window, same priority — will overlap with task1
    task4 = Task(
        title="Vet Checkup",
        category="Health",
        duration=1,
        priority=1,
        preferred_time_of_day="morning",
        pet_name="Buddy",
        frequency="once",
        due_date=date.today()
    )

    # Add tasks to pets
    dog.add_task(task1)
    dog.add_task(task3)
    dog.add_task(task4)  # conflicts with task1 — same window, same priority
    cat.add_task(task2)

    # Mark one task complete to test filtering + auto-rescheduling
    dog.complete_task(task3)  # weekly task — should auto-create next occurrence

    print("\n--- Buddy's tasks after completing Evening Play ---\n")
    for t in dog.tasks:
        print(f"  {t.title} | done: {t.completion_flag} | due: {t.due_date} | freq: {t.frequency}")

    # Create scheduler
    scheduler = Scheduler(owner=owner)

    # ------------------------------------------------------------------
    # Sorting — incomplete tasks ordered by window then priority
    # ------------------------------------------------------------------
    print("\n--- Sorted Incomplete Tasks (window → priority) ---\n")
    for t in scheduler.sort_tasks_by_priority_and_time():
        print(f"  [{t.preferred_time_of_day:<9}] priority {t.priority}  |  {t.title} ({t.pet_name})")

    # ------------------------------------------------------------------
    # Filter — incomplete tasks only
    # ------------------------------------------------------------------
    print("\n--- Filter: Incomplete Tasks Only ---\n")
    for t in scheduler.filter_tasks(completed=False):
        print(f"  {t.title} ({t.pet_name}) — done: {t.completion_flag}")

    # ------------------------------------------------------------------
    # Filter — completed tasks only
    # ------------------------------------------------------------------
    print("\n--- Filter: Completed Tasks Only ---\n")
    for t in scheduler.filter_tasks(completed=True):
        print(f"  {t.title} ({t.pet_name}) — done: {t.completion_flag}")

    # ------------------------------------------------------------------
    # Filter — tasks for Buddy only
    # ------------------------------------------------------------------
    print("\n--- Filter: Buddy's Tasks Only ---\n")
    for t in scheduler.filter_tasks(pet_name="Buddy"):
        print(f"  {t.title} — done: {t.completion_flag}")

    # ------------------------------------------------------------------
    # Generate and print schedule
    # ------------------------------------------------------------------
    schedule = scheduler.fit_tasks_into_schedule()

    print("\nToday's Schedule:\n")
    for task_title, pet_name, start, end in schedule:
        time_block = f"{start} - {end}"
        print(f"  {time_block:<22}  |  {task_title} ({pet_name})")

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------
    conflicts = scheduler.detect_conflicts(schedule)
    if conflicts:
        print("\n--- ⚠️  Schedule Conflicts Detected ---\n")
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("\n  ✅ No conflicts detected.")
    print()


if __name__ == "__main__":
    main()