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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**
<!-- 
- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
 -->

- I did use AI by giving it specific instructions and verifying suggested changes
- I used AI to create uml system diagram, implement classes from the diagram and create tests

**b. Judgment and verification**
<!-- 
- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
 -->

- I asked AI to create demo script and to output schedule to the terminal. Schedule created by AI did not have headers, so I asked to generate headers for attributes in schedule

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
