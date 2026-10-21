from datetime import time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


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
    walk = Task("Walk", 30, Priority.HIGH)
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
