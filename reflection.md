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

Yes. The first change happened early. When I had Claude review my skeleton code against my UML, it pointed out that once Owner.get_all_tasks() puts every pet's tasks into one list, there's no way to tell which pet a task belongs to. If I had two pets, the plan might just say "Feeding" twice and the explanation couldn't say whose it was. To fix this, I added a pet_name attribute to Task, and Pet.add_task() will fill it in when a task gets added. I used just the pet's name instead of the whole Pet object because a Pet already holds its tasks, so if each task also held its pet, printing either one would loop forever.

I also made Pet and Task dataclasses since they mostly just hold data, and kept Owner and Scheduler as regular classes. For the pet's task list I used field(default_factory=list) so each pet gets its own list instead of all pets sharing the same one.

In later phases I kept the same four classes, but they grew a lot. In Phase 2, Task got frequency and completed, plus mark_complete() and describe(), and Scheduler got sort_by_priority() and a skipped_tasks list so explain_plan() could say what didn't fit. In Phase 4, Task got a time, a due_date, and next_occurrence(), and its time and frequency started getting checked when a task is created. Pet got complete_task(), which marks a task done and adds its next copy, and Scheduler got sort_by_time(), filter_tasks(), and find_conflicts(). generate_plan() also changed so it only plans tasks due today or earlier. At the very end, Task got edit(), which lets the app change a task's details. It builds a temporary Task first so the same time and frequency checks run, and it keeps the task's pet and done/not-done status. My final diagram is in diagrams/uml_final.mmd.

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

I used Claude as my main coding assistant and GitHub Copilot as a second reviewer. Claude helped with almost every part of the project: drafting the UML, turning it into Python classes, writing the scheduling algorithms (sorting, filtering, recurring tasks, and conflict detection), connecting everything to the Streamlit app, writing the pytest tests, and debugging. Before committing, I often had Copilot look over Claude's work so I'd get a second opinion.

The most helpful prompts were the ones that set rules for how to work, not just what to build. For example: "don't modify any files yet, I want to review your plan first," "explain any changes before making them," and "run the tests and show me the actual results." Asking for a plan first meant I made the decisions myself. In Phase 4, I compared Claude's plan with Copilot's recommendations and then decided to store times as 24-hour "HH:MM" strings, add a "once" frequency, and leave app.py alone until later. Another really useful feature was that Claude could run things itself, like pytest, main.py, and a test version of the Streamlit app, so it reported real results instead of guessing.

I did the whole project in one long conversation with Claude, but I gave it one phase and step at a time. That kept each request small and made each change easier to check before moving on.

**b. Judgment and verification**

The clearest example was the recurring-task due dates. Claude's first version counted the next due date from the task's old due date, and it pointed out the side effect: finishing a daily task three days late would create a next copy that was already overdue. My class instructions said the next occurrence should be today + 1 day, so I didn't accept it as-is and asked for a fix. Now the next date counts from whichever is later, the due date or the day the task was finished. While fixing that, Claude also found that four of my existing tests only passed because they happened to run on Nov 1, so we gave them fixed completion dates.

Another example was the UML. Copilot noticed my diagram had duplicate class definitions, because a second copy of the diagram had ended up pasted inside the Task class. Instead of keeping the broken file, we rewrote it so each class was defined once and checked it against my original design.

Copilot also caught a missing requirement during my final review: the README said users should be able to add and edit tasks, but my app could only add and complete them. We added an Edit Task feature, using a new edit() method that runs the same checks as creating a task, plus three new tests, which brought the total to 45. A headless test of the new feature also showed that the dropdown jumped back to the first task after saving an edit, so we fixed that before finishing.

To check AI-generated code, I relied on tests and on actually running things: all 45 pytest tests pass, we ran main.py, and I tested the app in the browser. Running things caught bugs that looked fine on paper. In Phase 3, a headless test showed the app saying "Added …" while the task was really being saved to a copy of the pet, so it disappeared. Later, my browser showed AttributeError: 'Scheduler' object has no attribute 'sort_by_time'. I asked Claude to investigate before changing anything, and it turned out my Streamlit server had been running since before Phase 4, so it was still using the old Scheduler class. Restarting the server fixed it without any code changes.

---

## 4. Testing and Verification

**a. What you tested**

I have 45 pytest tests in tests/test_pawpal.py, and all of them pass. They're grouped by feature:

- Basic scheduling (6 tests): mark_complete() and add_task() work, high-priority tasks come first, the plan never goes over the available time, completed tasks are left out, and tasks from more than one pet get collected with the right pet_name.
- Sorting and times (6 tests): sort_by_time() puts tasks in time order with anytime tasks last and earlier dates first, a time like "8:05" gets stored as "08:05", bad times like "25:00" raise an error, and adding times doesn't change the priority-based plan.
- Filtering (4 tests): filtering by pet name, by done or not done, by both, and with no filters at all.
- Recurring tasks (12 tests): daily tasks come back 1 day later and weekly tasks 7 days later (even across the end of a month and year), "once" tasks don't repeat, complete_task() adds the next copy to the pet, completing the same task twice doesn't make a duplicate, late and early completion get the right next date, a bad frequency raises an error, and future tasks stay out of today's plan.
- Conflict detection (8 tests): two tasks at the same time for the same pet or for different pets, three tasks at one time giving one warning, no false warnings for different times, different dates, tasks without a time, or completed tasks, and checking just a list of tasks I pass in.
- Edge cases (6 tests): an owner with no pets or a pet with no tasks gets an empty plan and the "No tasks to schedule." message, nothing gets planned when no task fits in the time left, same-priority tasks go shortest first (but a short low-priority task still can't jump ahead of high ones), times like "9:00" and "10:00" sort in the right order, "8:00" and "08:00" still count as a conflict, and explain_plan() lists the chosen tasks, the total time, and the skipped ones.
- Editing tasks (3 tests): editing changes the real task instead of making a copy, keeps its pet and done/not-done status, and doesn't touch another task with the same title; invalid times or frequencies change nothing; and the scheduler, conflict check, and recurrence use the edited values.

I added the edge case tests after Claude and I went through my first 36 tests looking for gaps. To make sure they weren't just passing no matter what, I had Claude break the code on purpose in a few ways (like removing the shorter-first tiebreak and turning off the time formatting) and check that the new tests failed. Then the code was put back and all 42 passed again.

Most of the recurrence tests use fixed dates like date(2026, 11, 1) and pass in the completion date, so they give the same result no matter what day I run them. The few that check today's plan use dates relative to today, since the plan is always for today. We also ran main.py and checked the output by hand, and I tested the Streamlit app in the browser.

These tests are important because each one checks a promise the scheduler makes, like fitting in the owner's time, not repeating finished work, and not missing or making up conflicts. The date tests matter a lot because date bugs are easy to miss if you only ever run things on one day. While setting up the tests, running plain `pytest` couldn't find pawpal_system.py because the tests are in a subfolder, so we added a small pytest.ini that tells pytest to look in the project folder.

**b. Confidence**

I'd give it 4 out of 5. All 45 tests pass, including the edge cases like an empty schedule and tasks that don't fit, and the main.py output matched what I worked out by hand. So I'm pretty confident in the scheduling logic itself.

It's not a 5 for two reasons. First, my tests only cover pawpal_system.py, so the Streamlit app hasn't been tested automatically. It now has all the Phase 4 features, but I only checked those by hand in the browser. Second, find_conflicts() only catches tasks with the exact same start time, so overlapping tasks (like a 30-minute walk at 07:30 and training at 07:45) don't get a warning.

If I had more time, I would test:

- Priorities typed differently, like "High" or a typo (right now a typo gets ranked below low instead of causing an error)
- remove_task() when a pet has both an old completed copy and a new copy of the same recurring task (it removes the first one it finds)
- The Streamlit app itself, using Streamlit's testing tools
- Overlapping tasks, if I add duration-based conflict detection later

---

## 5. Reflection

**a. What went well**

I'm most satisfied that my original four-class design held up for the whole project. Every later feature (times, due dates, recurring tasks, filtering, and conflict warnings) fit into Owner, Pet, Task, and Scheduler without adding new classes. The Streamlit app now uses all of those features, and the scheduling logic is backed by 45 passing tests, including edge cases like an empty schedule and tasks that don't fit.

**b. What you would improve**

If I had another iteration, I would:

- Check for overlapping tasks using their durations, not just identical start times.
- Let users delete tasks in the app, and actually use owner preferences when scheduling.
- Save pets and tasks to a file so they don't disappear when the page refreshes.
- Give each task an ID. Right now the app finds tasks by pet name or by position in a list, and remove_task() works by title, which gets confusing once recurring tasks create copies with the same name.
- Add automated tests for the Streamlit app, not just the backend.

**c. Key takeaway**

My biggest takeaway is that AI can write a lot of code fast, but I'm still responsible for the design decisions. The recurring-task date logic passed its tests and still didn't match my class instructions, and the copied-Pet bug looked fine until the app actually ran. Even the AI made small mistakes, like adding an empty placeholder test by accident, and those only got caught because we kept checking. What worked best for me was asking for a plan first, making the decisions myself, and then checking the results with tests and by running the app instead of just trusting that the code looked right.
