from datetime import date, datetime, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

DAY_START = time(8, 0)
HEADERS = ("Time", "Done", "Task", "Pet", "Priority", "Frequency")
TASK_HEADERS = ("Time", "Done", "Task", "Pet", "Priority", "Due")


def print_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    """Print rows as a left-aligned table with a header and a dashed separator."""
    widths = [max(len(cell) for cell in column) for column in zip(headers, *rows)]

    def format_row(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(width) for cell, width in zip(cells, widths)).rstrip()

    print(format_row(headers))
    print(format_row(tuple("-" * width for width in widths)))
    for row in rows:
        print(format_row(row))


def print_schedule(owner: Owner, tasks: list[Task]) -> None:
    """Print tasks back to back, starting at DAY_START, as a table with headers."""
    today = date.today()
    start = datetime.combine(today, DAY_START)
    rows = []
    for task in tasks:
        end = start + timedelta(minutes=task.duration)
        rows.append(
            (
                f"{start:%H:%M}-{end:%H:%M}",
                "[x]" if task.completed else "[ ]",
                task.name,
                task.pet.name if task.pet else "-",
                task.priority.name,
                task.frequency.value,
            )
        )
        start = end

    print(f"Today's Schedule for {owner.first_name} {owner.last_name} - {today:%A, %B %d, %Y}")
    print()
    print_table(HEADERS, rows)


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print tasks in the given order, showing each task's own time (-- if it has none)."""
    print(f"\n{title}")
    if not tasks:
        print("(no matching tasks)")
        return
    rows = [
        (
            f"{task.time:%H:%M}" if task.time else "--:--",
            "[x]" if task.completed else "[ ]",
            task.name,
            task.pet.name if task.pet else "-",
            task.priority.name,
            f"{task.due_date:%Y-%m-%d}" if task.due_date else "today",
        )
        for task in tasks
    ]
    print_table(TASK_HEADERS, rows)


def main() -> None:
    owner = Owner("Jordan", "Lee")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of time and priority order on purpose, so the sorting is visible.
    # Two tasks share 09:00 (tie broken by priority) and one has no time (sorts last).
    mochi.add_task(Task("Evening walk", 30, Priority.MEDIUM, time=time(18, 30)))
    mochi.add_task(Task("Grooming", 45, Priority.LOW, Frequency.WEEKLY))
    luna.add_task(Task("Play session", 15, Priority.LOW, time=time(9, 0)))
    mochi.add_task(Task("Morning walk", 30, Priority.HIGH, time=time(7, 30)))
    luna.add_task(Task("Feeding", 10, Priority.HIGH, time=time(9, 0)))
    luna.add_task(Task("Litter box", 10, Priority.MEDIUM, time=time(12, 0)))

    scheduler = Scheduler(owner)
    print_tasks("As added (no sorting)", owner.get_all_tasks())

    # Completing a daily or weekly task queues its next occurrence automatically.
    # Grooming is weekly and Morning walk and Feeding are daily; a one-off would add nothing.
    print("\nmark_complete() on Morning walk, Feeding and Grooming")
    for task in list(owner.get_all_tasks()):
        if task.name in ("Morning walk", "Feeding", "Grooming"):
            next_task = task.mark_complete()
            print(f"{task.pet.name}'s {task.name} ({task.frequency.value}): next due {next_task.due_date}")
    print_tasks("After completing (new copies are pending and due later)", owner.get_all_tasks())
    print_tasks("sort_by_time()", scheduler.sort_by_time())
    print_tasks("filter_tasks(completed=False)", scheduler.filter_tasks(completed=False))
    print_tasks("filter_tasks(completed=True)", scheduler.filter_tasks(completed=True))
    print_tasks('filter_tasks(pet_name="luna")', scheduler.filter_tasks(pet_name="luna"))
    print_tasks(
        'filter_tasks(completed=False, pet_name="Mochi")',
        scheduler.filter_tasks(completed=False, pet_name="Mochi"),
    )
    print_tasks('filter_tasks(pet_name="Rex")', scheduler.filter_tasks(pet_name="Rex"))

    print()
    print_schedule(owner, scheduler.generate_daily_schedule())


if __name__ == "__main__":
    main()
