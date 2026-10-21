from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 30, Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_to_pet_increases_task_count():
    pet = Pet("Mochi", "dog")
    count_before = len(pet.tasks)

    pet.add_task(Task("Feeding", 10, Priority.MEDIUM))

    assert len(pet.tasks) == count_before + 1


def _scheduler_with(*tasks: Task) -> Scheduler:
    owner = Owner("Jordan", "Lee")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    for task in tasks:
        pet.add_task(task)
    return Scheduler(owner)


def test_sort_by_time_orders_earliest_first():
    evening = Task("Dinner", 10, Priority.HIGH, time=time(18, 0))
    morning = Task("Walk", 30, Priority.LOW, time=time(7, 30))
    noon = Task("Meds", 5, Priority.MEDIUM, time=time(12, 0))

    result = _scheduler_with(evening, morning, noon).sort_by_time()

    assert result == [morning, noon, evening]


def test_sort_by_time_puts_untimed_tasks_last():
    untimed = Task("Grooming", 45, Priority.HIGH)
    midnight = Task("Midnight meds", 5, Priority.LOW, time=time(0, 0))

    result = _scheduler_with(untimed, midnight).sort_by_time()

    assert result == [midnight, untimed]


def test_sort_by_time_breaks_ties_by_priority():
    low = Task("Play", 15, Priority.LOW, time=time(9, 0))
    high = Task("Feeding", 10, Priority.HIGH, time=time(9, 0))

    result = _scheduler_with(low, high).sort_by_time()

    assert result == [high, low]


def _owner_with_two_pets() -> tuple[Scheduler, Task, Task, Task]:
    owner = Owner("Jordan", "Lee")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    walk = Task("Walk", 30, Priority.HIGH, Frequency.ONCE)  # ONCE: completing it adds no copy
    bath = Task("Bath", 20, Priority.LOW)
    feed = Task("Feeding", 10, Priority.MEDIUM)
    mochi.add_task(walk)
    mochi.add_task(bath)
    luna.add_task(feed)
    walk.mark_complete()
    return Scheduler(owner), walk, bath, feed


def test_filter_tasks_without_filters_returns_everything():
    scheduler, walk, bath, feed = _owner_with_two_pets()

    assert scheduler.filter_tasks() == [walk, bath, feed]


def test_filter_tasks_by_completion_status():
    scheduler, walk, bath, feed = _owner_with_two_pets()

    assert scheduler.filter_tasks(completed=True) == [walk]
    assert scheduler.filter_tasks(completed=False) == [bath, feed]


def test_filter_tasks_by_pet_name_is_case_insensitive():
    scheduler, walk, bath, feed = _owner_with_two_pets()

    assert scheduler.filter_tasks(pet_name="mochi") == [walk, bath]
    assert scheduler.filter_tasks(pet_name=" LUNA ") == [feed]


def test_filter_tasks_combines_filters_and_handles_no_match():
    scheduler, walk, bath, feed = _owner_with_two_pets()

    assert scheduler.filter_tasks(completed=False, pet_name="Mochi") == [bath]
    assert scheduler.filter_tasks(pet_name="Rex") == []


def test_completing_daily_task_creates_next_day_occurrence_on_same_pet():
    pet = Pet("Mochi", "dog")
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY, time=time(7, 30), due_date=date(2026, 10, 20))
    pet.add_task(walk)

    next_walk = walk.mark_complete()

    assert walk.completed is True
    assert next_walk is not walk
    assert next_walk.completed is False
    assert next_walk.due_date == date(2026, 10, 21)
    assert (next_walk.name, next_walk.duration, next_walk.priority) == ("Walk", 30, Priority.HIGH)
    assert (next_walk.frequency, next_walk.time) == (Frequency.DAILY, time(7, 30))
    assert next_walk.pet is pet
    assert pet.tasks == [walk, next_walk]


def test_completing_weekly_task_creates_occurrence_seven_days_later():
    pet = Pet("Mochi", "dog")
    bath = Task("Bath", 20, Priority.LOW, Frequency.WEEKLY, due_date=date(2026, 10, 28))
    pet.add_task(bath)

    next_bath = bath.mark_complete()

    assert next_bath.due_date == date(2026, 11, 4)  # rolls over the month boundary


def test_completing_task_without_due_date_schedules_next_from_today():
    task = Task("Feeding", 10, Priority.MEDIUM, Frequency.DAILY)

    next_task = task.mark_complete()

    assert next_task.due_date == date.today() + timedelta(days=1)


def test_completing_one_off_task_creates_no_new_occurrence():
    pet = Pet("Mochi", "dog")
    vet = Task("Vet visit", 60, Priority.HIGH, Frequency.ONCE)
    pet.add_task(vet)

    assert vet.mark_complete() is None
    assert pet.tasks == [vet]


def test_completing_a_task_twice_does_not_create_duplicates():
    pet = Pet("Mochi", "dog")
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY)
    pet.add_task(walk)

    walk.mark_complete()
    assert walk.mark_complete() is None

    assert len(pet.tasks) == 2


def test_task_not_on_a_pet_still_returns_next_occurrence():
    next_task = Task("Walk", 30, Priority.HIGH, Frequency.DAILY).mark_complete()

    assert next_task.pet is None


def test_daily_schedule_excludes_tasks_due_in_the_future():
    today = date(2026, 10, 20)
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY, due_date=today)
    overdue = Task("Meds", 5, Priority.MEDIUM, due_date=date(2026, 10, 18))
    undated = Task("Feeding", 10, Priority.LOW)
    scheduler = _scheduler_with(walk, overdue, undated)

    next_walk = walk.mark_complete()
    schedule = scheduler.generate_daily_schedule(today=today)

    assert next_walk not in schedule
    assert schedule == [overdue, undated]
    assert scheduler.generate_daily_schedule(today=date(2026, 10, 21)) == [next_walk, overdue, undated]


def test_find_conflicts_flags_same_start_time_for_different_pets():
    owner = Owner("Jordan", "Lee")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    walk = Task("Walk", 30, Priority.HIGH, time=time(9, 0))
    feed = Task("Feeding", 10, Priority.MEDIUM, time=time(9, 0))
    mochi.add_task(walk)
    luna.add_task(feed)

    assert Scheduler(owner).find_conflicts() == [(walk, feed)]


def test_find_conflicts_flags_overlap_for_the_same_pet():
    walk = Task("Walk", 30, Priority.HIGH, time=time(9, 0))
    bath = Task("Bath", 20, Priority.LOW, time=time(9, 15))

    assert _scheduler_with(bath, walk).find_conflicts() == [(walk, bath)]


def test_find_conflicts_ignores_back_to_back_tasks():
    walk = Task("Walk", 30, Priority.HIGH, time=time(9, 0))
    feed = Task("Feeding", 10, Priority.MEDIUM, time=time(9, 30))

    assert _scheduler_with(walk, feed).find_conflicts() == []


def test_find_conflicts_ignores_completed_and_untimed_tasks():
    walk = Task("Walk", 30, Priority.HIGH, time=time(9, 0))
    done = Task("Feeding", 10, Priority.MEDIUM, Frequency.ONCE, time=time(9, 0))
    untimed = Task("Grooming", 45, Priority.LOW)
    done.mark_complete()

    assert _scheduler_with(walk, done, untimed).find_conflicts() == []


def test_find_conflicts_catches_a_long_task_spanning_several_later_ones():
    long_task = Task("Training", 120, Priority.HIGH, time=time(9, 0))
    early = Task("Feeding", 10, Priority.MEDIUM, time=time(9, 30))
    late = Task("Meds", 5, Priority.LOW, time=time(10, 30))
    after = Task("Play", 15, Priority.LOW, time=time(11, 0))

    conflicts = _scheduler_with(after, late, early, long_task).find_conflicts()

    assert conflicts == [(long_task, early), (long_task, late)]


def test_find_conflicts_ignores_same_time_on_different_days():
    today = date(2026, 10, 20)
    walk = Task("Walk", 30, Priority.HIGH, time=time(9, 0), due_date=today)
    tomorrows_walk = walk.mark_complete()

    assert _scheduler_with(walk, tomorrows_walk).find_conflicts(today=today) == []
    # An undated task counts as due today, so it does clash with a dated task on that day.
    undated = Task("Feeding", 10, Priority.LOW, time=time(9, 0))
    dated = Task("Meds", 5, Priority.LOW, time=time(9, 5), due_date=today)
    assert _scheduler_with(undated, dated).find_conflicts(today=today) == [(undated, dated)]


def test_find_conflicts_catches_a_task_running_past_midnight():
    today = date(2026, 10, 20)
    late = Task("Vigil", 90, Priority.HIGH, time=time(23, 30), due_date=today)
    early = Task("Meds", 5, Priority.LOW, time=time(0, 30), due_date=date(2026, 10, 21))

    assert _scheduler_with(late, early).find_conflicts() == [(late, early)]


def test_conflict_warnings_describe_each_overlap_without_raising():
    owner = Owner("Jordan", "Lee")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Walk", 30, Priority.HIGH, time=time(9, 0)))
    luna.add_task(Task("Feeding", 10, Priority.MEDIUM, time=time(9, 5)))
    mochi.add_task(Task("Bath", 20, Priority.LOW, time=time(9, 20)))

    warnings = Scheduler(owner).conflict_warnings()

    assert warnings == [
        "Warning (different pets): Mochi's Walk (09:00-09:30) overlaps Luna's Feeding (09:05-09:15)",
        "Warning (same pet): Mochi's Walk (09:00-09:30) overlaps Mochi's Bath (09:20-09:40)",
    ]


def test_conflict_warnings_is_empty_when_nothing_overlaps():
    walk = Task("Walk", 30, Priority.HIGH, time=time(9, 0))
    feed = Task("Feeding", 10, Priority.MEDIUM, time=time(10, 0))

    assert _scheduler_with(walk, feed).conflict_warnings() == []
    assert Scheduler(Owner("Jordan", "Lee")).conflict_warnings() == []
