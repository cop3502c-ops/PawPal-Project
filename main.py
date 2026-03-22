from pawpal_system import Task, Pet, Owner, Scheduler


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
        pet_name="Buddy"
    )

    task2 = Task(
        title="Feed Cat",
        category="Feeding",
        duration=2,
        priority=1,
        preferred_time_of_day="morning",
        pet_name="Whiskers"
    )

    task3 = Task(
        title="Evening Play",
        category="Enrichment",
        duration=2,
        priority=3,
        preferred_time_of_day="evening",
        pet_name="Buddy"
    )

    # Add tasks to pets
    dog.add_task(task1)
    dog.add_task(task3)
    cat.add_task(task2)

    # Create scheduler
    scheduler = Scheduler(owner=owner)

    # Generate and print schedule
    schedule = scheduler.fit_tasks_into_schedule()

    print("\nToday's Schedule:\n")
    for task_title, pet_name, start, end in schedule:
        time_block = f"{start} - {end}"
        print(f"  {time_block:<22}  |  {task_title} ({pet_name})")
    print()


if __name__ == "__main__":
    main()