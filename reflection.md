# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML modeled PawPal+ as four core classes, each with a single clear responsibility:

- **Owner** — represents the person using the app. It holds the owner's `name`, a list of their `pets`, and a `preferences` dictionary, with `add_pet()` and `list_pets()` to manage the pets it owns. Its job is to be the top-level container for who is being served and what they care about.
- **Pet** — represents an individual animal. It holds a `name`, `species`, and its own list of care `tasks`, with `add_task()` and `list_tasks()`. Its job is to own the care activities that belong to that specific animal.
- **Task** — represents a single care activity (a walk, feeding, meds, etc.). It holds a `title`, `duration_minutes`, and a `priority`, plus a `priority_weight()` method that converts the text priority into a number. Its job is to be the smallest unit of work the scheduler reasons about.
- **Scheduler** — the "brain." It holds the available `day_minutes` budget and exposes `build_schedule(tasks)` to pick and order tasks that fit the day, plus `explain()` to describe why it produced that plan. Its job is all of the scheduling logic, kept separate from the data classes.

The relationships were: an Owner owns many Pets, a Pet needs many Tasks, and the Scheduler *uses* Tasks (a dependency, not ownership) to produce a plan. I deliberately kept the Scheduler decoupled from Owner/Pet so it operates on a flat list of Tasks rather than reaching into the object graph.

**b. Design changes**

Yes. The most important change was giving **Task** a `priority_weight()` method instead of storing priority directly as a number. My first instinct was to store `priority` as an `int` so the scheduler could sort on it immediately. During implementation I realized that made the data harder to read and enter — the UI and the owner think in terms of "low / medium / high," not "1 / 2 / 3." So I kept `priority` as a human-readable `str` and added `priority_weight()` to translate it to a number only when the scheduler needs to sort. This keeps the stored data user-friendly while still giving the Scheduler a clean numeric key, and it isolates the mapping in one place so I can tune the weights later without touching the sorting logic.

A second, smaller change was keeping the **Scheduler** as its own class rather than putting `build_schedule()` on Owner. Early on it was tempting to let the Owner "just schedule its pets," but separating the Scheduler kept the scheduling policy independent of who owns the pets, made it easy to pass in any list of tasks, and made the logic far simpler to unit-test in isolation.

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
