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

**a. Which AI features were most effective for building the scheduler**

A few features of my AI coding assistant did the most work:

- **Codebase-aware edits.** Because the assistant could read the whole repo, it kept `app.py`,
  `main.py`, `pawpal_system.py`, and the tests consistent when a method signature changed. When I
  renamed or reshaped a `Scheduler` method, it updated every call site instead of leaving me to
  hunt for them.
- **Grounding answers in the actual code.** The most effective prompts were specific and
  code-anchored — e.g. "name the exact method that implements conflict detection and describe its
  behavior" — rather than open-ended "how should I build a scheduler." Pointing it at real methods
  like `find_conflicts()` and `build_schedule()` kept its output accurate instead of inventing an
  API.
- **Test scaffolding.** It was fast at turning a described behavior ("a daily task's next
  occurrence is due one day later") into a concrete pytest case, which let me focus on deciding
  *what* to test rather than boilerplate.
- **Explaining tradeoffs on request.** Asking it to lay out the pros and cons of a design choice
  (before writing code) was more useful than asking it to just pick one.

**b. An AI suggestion I rejected or modified to keep the design clean**

My original UML modeled a `Task` with `duration_minutes` and a `priority` weight, and a
`Scheduler` with a `day_minutes` budget — and the assistant was happy to build a "fit as many
high-priority tasks as possible into the available minutes" scheduler around that. I rejected that
direction. For a pet-care assistant, an owner thinks in terms of *when* things happen ("walk at
08:00, feed at 07:30"), not in terms of packing minutes into a daily budget, and the
duration/priority model added state I couldn't test cleanly or explain simply. I redesigned `Task`
around `time` and `frequency` instead, dropped `day_minutes` entirely, and made the scheduler sort
by time of day with exact-time conflict detection. The result is a model that matches how the app
is actually used and is far easier to verify. I evaluated the change by writing the tests first:
the time-based model produced small, deterministic assertions (e.g. sorted `["07:30", "12:00",
"18:00"]`), whereas the minute-packing version would have needed fuzzy "did it pick a reasonable
set" checks.

I also verified AI output the same way throughout: I ran `python -m pytest` and `python main.py`
after each change rather than trusting that generated code was correct, and I read every diff
before accepting it.

**c. How separate chat sessions per phase kept me organized**

I used a different session for each phase — design/UML, implementing `pawpal_system.py`, writing
tests, and wiring up the Streamlit UI. This helped in two concrete ways. First, each session
stayed focused: the implementation session had the class design fresh in context and didn't drag
in unrelated UI concerns, so its suggestions were more on-target. Second, it gave me a natural
checkpoint between phases — I had to restate the current design when starting the next session,
which forced me to confirm the code actually matched my mental model (this is exactly how I caught
that the UML still described the old `duration_minutes` design after I'd moved to a time-based
one). Keeping sessions scoped also made it easy to go back and find the reasoning behind a specific
decision instead of scrolling through one giant thread.

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
