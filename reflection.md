# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Owner — the central user of the app. Responsible for managing a collection of pets and owning a personal scheduler.

Pet — represents an individual animal. Responsible for storing profile data (species, breed, age, weight) and maintaining its own medical history.

Task — a single care action (feeding, grooming, vet visit, etc.). Responsible for tracking what needs to be done, when, for which pet, how often, and its current status.

Scheduler — the organizational hub. Responsible for holding all tasks, retrieving upcoming or overdue tasks, and triggering reminders.

MedicalRecord — a data record attached to a pet. Responsible for storing vet visit details and health notes over time.

Notification — a reminder tied to a task. Responsible for being sent or cancelled at a scheduled time.

TaskStatus (enum) — defines the state of a task: PENDING, COMPLETED, OVERDUE, or CANCELLED.

Frequency (enum) — defines how often a task repeats: ONCE, DAILY, WEEKLY, or MONTHLY.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, one change being the addition of python dataclasses for medical record, notification, pet, and task. This was to add more functionality to the website 

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

An example being time, two tasks cant physicaly happen at the same time, so a missed priority ranking is inconvenient. The general principle was that constraints were added in order of impact if violated — time conflicts cause real harm, priority misordering causes friction, and status filtering is just correctness hygiene.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

every task is compared against every other task. A more efficient approach would sort tasks first and break the inner loop early once no further overlaps are possible

- Why is that tradeoff reasonable for this scenario?

Because a pet owner realistically schedules tens of tasks, not thousands. At that scale, the algorithm runs in microseconds and the simpler nested loop is easier to read, debug, and explain than a sort-and-break optimization would be

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used it to help generate a mermaid diagram, general designing and brainstorming. Especially when trying to implement the classes into the code was where it was most useful

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I felt the ai overly complicated the task class with the mermaid design and how it was trying to implement into the code, I had to tell it to keep it simple (2 tasks max for each pet)

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Sorting correctness, recurring task, and conflict detection

- Why were these tests important?
These three behaviors are the ones a pet owner would notice immediately if they broke. If sorting is wrong, the schedule is unreadable.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Considering the tests all passed when running pytests, i feel pretty confident

- What edge cases would you test next if you had more time?
Adding a bunch of tasks and tying it to one dog to see what happens

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The ai understood what i asked of it almost immediately. Adding the features to the site felt satisfying.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
Connect it to google calendar for the scheduler, add pictures of the pets, maybe have different sets of tasks available for the different pets.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Using ai can help make testing your code much more simple, making debugging a breeze.