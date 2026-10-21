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
