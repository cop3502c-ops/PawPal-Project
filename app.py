from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (hours)", min_value=0.25, max_value=8.0, value=1.0, step=0.25)
with col3:
    priority = st.number_input("Priority (1 = highest)", min_value=1, max_value=10, value=1)

time_of_day = st.selectbox("Time of day", ["morning", "afternoon", "evening"])
category = st.text_input("Category", value="Exercise")
frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])  # new

if st.button("Add task"):
    st.session_state.tasks.append({
        "title":                 task_title,
        "category":              category,
        "duration":              float(duration),
        "priority":              int(priority),
        "preferred_time_of_day": time_of_day,
        "pet_name":              pet_name,
        "frequency":             frequency,  # new
    })

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)

    st.markdown("### Mark Task Complete")
    task_titles = [t["title"] for t in st.session_state.tasks
                   if not t.get("completed", False)]
    if task_titles:
        selected = st.selectbox("Select a task to mark complete", task_titles)
        if st.button("Mark Complete"):
            for t in st.session_state.tasks:
                if t["title"] == selected and not t.get("completed", False):
                    t["completed"] = True
                    # Auto-create next occurrence for recurring tasks
                    if t.get("frequency") in ("daily", "weekly"):
                        from datetime import date, timedelta
                        current_due = t.get("due_date", date.today())
                        if isinstance(current_due, str):
                            current_due = date.today()
                        next_due = current_due + (
                            timedelta(days=1) if t["frequency"] == "daily"
                            else timedelta(weeks=1)
                        )
                        st.session_state.tasks.append({
                            "title":                 t["title"],
                            "category":              t["category"],
                            "duration":              t["duration"],
                            "priority":              t["priority"],
                            "preferred_time_of_day": t["preferred_time_of_day"],
                            "pet_name":              t["pet_name"],
                            "frequency":             t["frequency"],
                            "due_date":              next_due,
                            "completed":             False,
                        })
                        st.success(f"'{selected}' marked complete! Next occurrence created for {next_due}.")
                    else:
                        st.success(f"'{selected}' marked complete!")
                    break
            st.rerun()
    else:
        st.info("All tasks are complete!")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button calls your scheduling logic.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Build owner
        owner = Owner(name=owner_name, available_time=(8, 18))

        # Build one Pet per unique pet_name in tasks
        pets = {}
        for t in st.session_state.tasks:
            if t["pet_name"] not in pets:
                pets[t["pet_name"]] = Pet(name=t["pet_name"], species=species, age=0, care_notes="")

        for t in st.session_state.tasks:
            if t.get("completed", False):
                continue
            task = Task(
                title=t["title"],
                category=t["category"],
                duration=t["duration"],
                priority=t["priority"],
                preferred_time_of_day=t["preferred_time_of_day"],
                pet_name=t["pet_name"],
                frequency=t["frequency"],
                due_date=date.today(),
            )
            pets[t["pet_name"]].add_task(task)

        for pet in pets.values():
            owner.add_pet(pet)

        scheduler = Scheduler(owner=owner)
        schedule  = scheduler.fit_tasks_into_schedule()

        if not schedule:
            st.error("No tasks could be scheduled. Check durations and time of day.")
        else:
            st.success("Schedule generated!")
            st.markdown("### Today's Schedule")
            for title, pname, start, end in schedule:
                st.markdown(f"🕐 **{start} – {end}** &nbsp;|&nbsp; {title} *({pname})*")

            # Conflict detection — new
            conflicts = scheduler.detect_conflicts(schedule)
            if conflicts:
                st.markdown("### ⚠️ Conflicts Detected")
                for warning in conflicts:
                    st.warning(warning)
            else:
                st.success("✅ No conflicts detected.")

#python -m streamlit run app.py runs the game