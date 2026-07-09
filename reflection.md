# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

    - **Owner** — represents the person using the app. It holds the owner's `name`, a list of their `pets`, and a `preferences` dictionary, with `add_pet()` and `list_pets()` to manage the pets it owns. Its job is to be the top-level container for who is being served and what they care about.
    - **Pet** — represents an individual animal. It holds a `name`, `species`, and its own list of care `tasks`, with `add_task()` and `list_tasks()`. Its job is to own the care activities that belong to that specific animal.
    - **Task** — represents a single care activity (a walk, feeding, meds, etc.). It holds a `title`, `duration_minutes`, and a `priority`, plus a `priority_weight()` method that converts the text priority into a number. Its job is to be the smallest unit of work the scheduler reasons about.
    - **Scheduler** — the "brain." It holds the available `day_minutes` budget and exposes `build_schedule(tasks)` to pick and order tasks that fit the day, plus `explain()` to describe why it produced that plan. Its job is all of the scheduling logic, kept separate from the data classes.

     => The relationships were: an Owner owns many Pets, a Pet needs many Tasks, and the Scheduler *uses* Tasks (a dependency, not ownership) to produce a plan. I deliberately kept the Scheduler decoupled from Owner/Pet so it operates on a flat list of Tasks rather than reaching into the object graph.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

My scheduler detects conflicts by **exact start-time match only, not by overlapping durations**. In `find_conflicts()`, I group every task by its `time` string ("HH:MM") and flag any slot that holds two or more tasks. So two tasks both set for 08:00 are correctly reported as a clash, but a 45-minute walk starting at 08:00 that runs into an 08:30 feeding is *not* flagged, because the scheduler has no concept of duration — a `Task` only stores a start `time`, not how long it lasts.

This tradeoff is reasonable for this scenario for two reasons. First, it matches the data I actually model: pet care tasks are entered as "the thing that happens at this time" (walk at 08:00, meds at 07:30), and most everyday routines are short and spaced out, so exact-time collisions catch the conflicts an owner realistically hits. Second, it keeps the model and the logic simple and easy to test — grouping by a string key is O(n), unambiguous, and has no edge cases around how overlap is defined, whereas true interval-overlap detection would require adding durations to every task, deciding how to handle back-to-back vs. truly overlapping slots, and more complex comparisons. Given a busy owner who mainly needs "don't double-book me at the same moment," exact-match conflict detection delivers the most value for the least complexity. Adding duration-aware overlap detection is a natural next iteration if the app needs finer scheduling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
