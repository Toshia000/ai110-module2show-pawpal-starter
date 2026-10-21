from pawpal_system import Pet, Priority, Task


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
