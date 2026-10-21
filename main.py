from datetime import date, datetime, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

DAY_START = time(8, 0)
HEADERS = ("Time", "Done", "Task", "Pet", "Priority", "Frequency")


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

    widths = [max(len(cell) for cell in column) for column in zip(HEADERS, *rows)]

    def format_row(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(width) for cell, width in zip(cells, widths)).rstrip()

    print(f"Today's Schedule for {owner.first_name} {owner.last_name} - {today:%A, %B %d, %Y}")
    print()
    print(format_row(HEADERS))
    print(format_row(tuple("-" * width for width in widths)))
    for row in rows:
        print(format_row(row))


def main() -> None:
    owner = Owner("Jordan", "Lee")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of priority order on purpose, so the scheduler's sorting is visible.
    mochi.add_task(Task("Grooming", 45, Priority.LOW, Frequency.WEEKLY))
    mochi.add_task(Task("Morning walk", 30, Priority.HIGH))
    luna.add_task(Task("Feeding", 10, Priority.MEDIUM))

    schedule = Scheduler(owner).generate_daily_schedule()
    print_schedule(owner, schedule)


if __name__ == "__main__":
    main()
