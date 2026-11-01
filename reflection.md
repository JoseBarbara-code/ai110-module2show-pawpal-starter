# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design has four classes: Owner, Pet, Task, and Scheduler.

Owner: Stores the owner's name, how many minutes they have available in the day, their preferences, and a list of their pets. It can add a pet and gather up all the tasks from every pet.

Pet: Stores basic information about the pet, such as its name and species, and keeps track of its tasks. It can add or remove a task.

Task: Stores one pet care activity like a walk, feeding, or grooming, along with how long it takes and its priority (low, medium, or high). It has a priority_rank() method that turns the priority into a number so tasks can be sorted.

Scheduler: Takes the owner and organizes their tasks into a daily schedule based on the owner's available time and task priorities. It can also explain why it picked the tasks it did.

For the relationships, an owner can have many pets, each pet can have many tasks, and the scheduler goes through the owner to get to the tasks. I chose these classes because they cover everything that is needed without making it too complicated.

**b. Design changes**

Yes, a little. When I compared my skeleton code to my UML, I noticed that once Owner.get_all_tasks() puts every pet's tasks into one list, there's no way to tell which pet a task belongs to. If I had two pets, the plan might just say "Feeding" twice and the explanation couldn't say whose it was. To fix this, I added a pet_name attribute to Task, and Pet.add_task() will fill it in when a task gets added. I used just the pet's name instead of the whole Pet object because a Pet already holds its tasks, so if each task also held its pet, printing either one would loop forever.

I also made Pet and Task dataclasses since they mostly just hold data, and kept Owner and Scheduler as regular classes. For the pet's task list I used field(default_factory=list) so each pet gets its own list instead of all pets sharing the same one.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler looks at these things:

- Available time: the owner's available_minutes is a hard limit. The total time of the planned tasks never goes over it.
- Priority: tasks are sorted high, then medium, then low. priority_rank() turns these into 3, 2, and 1 so they can be sorted.
- Duration: when two tasks have the same priority, the shorter one goes first so more tasks can fit.
- Completion: tasks that are already marked complete are left out of the plan.
- Due date: every task has a due_date. The plan only includes tasks due today or earlier, so a task I missed yesterday still shows up, but tomorrow's tasks wait for their own day.
- Scheduled time: a task can have a time like "07:30", or no time if it can be done anytime. The time doesn't change which tasks get picked. sort_by_time() puts the chosen tasks in order for the day, and find_conflicts() uses the time to warn me about two tasks at the same time.

Daily and weekly recurrence works now too. When I finish a task with Pet.complete_task(), it adds a new copy for the next day (daily) or a week later (weekly), and "once" tasks don't repeat. Owner preferences are still stored, but the scheduler doesn't use them.

I decided time mattered most because the owner can't do more than they have time for, so the plan has to fit no matter what. After that, priority made the most sense because things like feeding and walks are more important than play time. Duration is only used as a tiebreaker.

**b. Tradeoffs**

The biggest tradeoff is in my conflict detection. find_conflicts() only warns when two tasks are at the exact same date and time. It doesn't look at how long the tasks take, so it can miss overlaps. In my demo, Mochi's Morning walk starts at 07:30 and lasts 30 minutes, and Training starts at 07:45. Those really do overlap, but there's no warning because the start times are different. Checking for overlaps would mean figuring out each task's end time and comparing tasks against each other, which is more code and more places for bugs. I think exact matches are a reasonable start for this project because they catch the most obvious mistake (two things booked at the same time), and the check is easy to understand and test. The warning also doesn't move or drop anything, so the owner still decides what to do about it.

The plan itself is also greedy. It goes through the tasks once from highest to lowest priority and takes each one that fits in the time left, instead of trying every combination to use the most time. In my demo, after the high-priority tasks there were 15 minutes left. It picked Brush fur (medium, 10 min), and then neither 15-minute low-priority task fit, so 5 minutes went unused. A low-priority task would have filled the time exactly, but then a medium task would have been skipped for a low one. I'm okay with that because getting the important tasks done matters more than using every minute.

One thing I had to keep straight is that priority and time do different jobs. Priority decides which tasks make it into the plan, and sort_by_time() only changes the order they're shown in. So giving a task an early time doesn't help it get picked, and the plan doesn't check whether two chosen tasks clash. That's what the separate conflict warning is for.

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

I have 36 pytest tests in tests/test_pawpal.py, and all of them pass. They're grouped by feature:

- Basic scheduling (6 tests): mark_complete() and add_task() work, high-priority tasks come first, the plan never goes over the available time, completed tasks are left out, and tasks from more than one pet get collected with the right pet_name.
- Sorting and times (6 tests): sort_by_time() puts tasks in time order with anytime tasks last and earlier dates first, a time like "8:05" gets stored as "08:05", bad times like "25:00" raise an error, and adding times doesn't change the priority-based plan.
- Filtering (4 tests): filtering by pet name, by done or not done, by both, and with no filters at all.
- Recurring tasks (12 tests): daily tasks come back 1 day later and weekly tasks 7 days later (even across the end of a month and year), "once" tasks don't repeat, complete_task() adds the next copy to the pet, completing the same task twice doesn't make a duplicate, late and early completion get the right next date, a bad frequency raises an error, and future tasks stay out of today's plan.
- Conflict detection (8 tests): two tasks at the same time for the same pet or for different pets, three tasks at one time giving one warning, no false warnings for different times, different dates, tasks without a time, or completed tasks, and checking just a list of tasks I pass in.

Most of the recurrence tests use fixed dates like date(2026, 11, 1) and pass in the completion date, so they give the same result no matter what day I run them. The few that check today's plan use dates relative to today, since the plan is always for today. I also ran main.py and checked the output by hand.

These tests are important because each one checks a promise the scheduler makes, like fitting in the owner's time, not repeating finished work, and not missing or making up conflicts. The date tests matter a lot because date bugs are easy to miss if you only ever run things on one day. While setting up the tests, running plain `pytest` couldn't find pawpal_system.py because the tests are in a subfolder, so I added a small pytest.ini that tells pytest to look in the project folder.

**b. Confidence**

I'm pretty confident in the scheduling logic now. All 36 tests pass, they cover every Phase 4 feature, and the main.py output matched what I worked out by hand. I'm less sure about the Streamlit app, because my tests only cover pawpal_system.py and not app.py, and the app doesn't use the new Phase 4 features yet.

There's also a limit I already know about: find_conflicts() only catches tasks with the exact same start time, so overlapping tasks (like a 30-minute walk at 07:30 and training at 07:45) don't get a warning.

If I had more time, I would test:

- An owner with 0 available minutes, or with no pets or tasks
- Priorities typed differently, like "High" or a typo (right now a typo gets ranked below low instead of causing an error)
- remove_task() when a pet has both an old completed copy and a new copy of the same recurring task (it removes the first one it finds)
- The text that explain_plan() returns
- The Streamlit app itself

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
