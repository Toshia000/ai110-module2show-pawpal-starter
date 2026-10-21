# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
<!-- 
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
 -->

- Essential features:
  - Add a pet
  - Create a task
  - View tasks for today
- UML design includes four classes Owner, Pet, Task and Scheduler. Owner has attributes: first and last names and a list of pets. Owner has methods to add new pets and list all tasks. Pet has attributes: name, species, owner and a list of tasks. Pet has a method to add new tasks. Task has attributes: task name, duration, priority and assigned pet. Task has a method to mark task a complete. Scheduler has attribute: assigned owner. Scheduler has a method to sort tasks by priority and generate daily schedule.

**b. Design changes**
<!-- 
- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
 -->

- Scheduler does not include attribute with list of all tasks. It uses owner class to get all tasks.
- Task includes frequency and completion status
- Task has a method to mark task as complete
- Task also got an optional time of day and an optional due date. Conflict detection and recurring tasks both need them
- Priority and Frequency are enums (HIGH, MEDIUM, LOW and once, daily, weekly) instead of plain strings, so a typo can't create an invalid value
- `mark_complete` now returns the next occurrence for daily and weekly tasks and adds it to the same pet. Completing a task twice returns nothing, so it can't create duplicates
- Scheduler grew from sorting by priority to also sort by time, filter by completion and pet name, find conflicts and write conflict warnings
- Tasks, pets and owners compare by identity (`eq=False`), so two tasks that look the same stay separate. They also point back to their pet or owner, and `add_task` and `add_pet` keep both sides in sync

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers priority, time of day, due date and completion status. It does not use a daily time budget or owner preferences
- Priority matters most for the daily schedule: it keeps pending tasks due today or earlier and orders them HIGH first
- Time of day is used for sorting and conflict detection, but not for ordering the daily schedule, which stacks tasks back to back from 08:00 in priority order
- Due date decides which tasks are left out: tomorrow's copy of a daily task does not show up today, while overdue tasks stay in

**b. Tradeoffs**
<!-- 
- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
 -->

- There is an assumption that person does one thing at a time, even when it is possible to feed or walk multiple pets at a time
- Conflicts only warn. Nothing blocks adding an overlapping task, so the app keeps running and the owner decides what to do. This is reasonable because the owner can sometimes do two things at once
- Only timed, pending tasks are checked for conflicts. Completed tasks, untimed tasks and tasks on different days are ignored
- Recurrence counts from the due date, not from when the task was finished. A task completed late keeps its cadence, but its next copy can already be overdue. Completed copies also pile up in the task list
- Conflict detection sorts tasks by start time and compares each one only with tasks that start before it ends. That is faster than comparing every pair, but it is harder to read

---

## 3. AI Collaboration

**a. How you used AI**
<!-- 
- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
 -->

- I did use AI by giving it specific instructions and verifying suggested changes
- I used AI to create uml system diagram, implement classes from the diagram and create tests
- I also used AI to list edge cases for sorting and recurring tasks, then to draft tests for them and a README demo walkthrough from the real `main.py` output

**b. Judgment and verification**
<!-- 
- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
 -->

- I asked AI to create demo script and to output schedule to the terminal. Schedule created by AI did not have headers, so I asked to generate headers for attributes in schedule

---

## 4. Testing and Verification

**a. What you tested**

- The suite has 47 tests in `tests/test_pawpal.py`, all passing
- Sorting: priority order, time order, untimed tasks last, ties broken by priority and then insertion order, empty owners, and time of day compared without the due date
- Filtering: by completion, by pet name (case-insensitive) and both together
- Recurring tasks: daily and weekly copies, one-off tasks, completing twice, tasks with no due date, late completion, chains of copies, and month, year and leap-day boundaries
- Conflict detection: overlaps for the same pet and different pets, back-to-back tasks, a long task covering several others, three-way overlaps, tasks running past midnight, and ignoring completed or untimed tasks
- These matter because the scheduler's value is its rules. A wrong ordering or a missed overlap would look fine in the UI and still give the owner a bad plan

**b. Confidence**

- I am fairly confident in sorting, filtering, recurrence and conflict detection, since the main cases and boundaries are tested
- The Streamlit app is not tested, and it does not yet expose times, frequency, completion or conflict warnings
- Next I would test a task with zero duration. Its conflict result depends on whether it sorts before or after the longer task, so the same overlap is reported or missed depending on priority
- I would also test negative durations, which are not validated, and very many tasks that all overlap, where the number of reported pairs grows quickly

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
