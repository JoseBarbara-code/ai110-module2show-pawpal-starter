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

My scheduler looks at four things:

- Available time: the owner's available_minutes is a hard limit. The total time of the planned tasks never goes over it.
- Priority: tasks are sorted high, then medium, then low. priority_rank() turns these into 3, 2, and 1 so they can be sorted.
- Duration: when two tasks have the same priority, the shorter one goes first so more tasks can fit.
- Completion: tasks that are already marked complete are left out of the plan.

Owner preferences and task frequency (daily or weekly) are stored, but the scheduler doesn't use them yet. It also doesn't give tasks a time of day yet, so the plan is just an order.

I decided time mattered most because the owner can't do more than they have time for, so the plan has to fit no matter what. After that, priority made the most sense because things like feeding and walks are more important than play time. Duration is only used as a tiebreaker.

**b. Tradeoffs**

My scheduler is greedy. It goes down the sorted list once and takes each task that fits in the time left. It doesn't try every combination to find the one that uses the most time. You can see this in my demo: after the high-priority tasks there were 15 minutes left. The scheduler picked Brush fur (medium, 10 min) and then couldn't fit either of the 15-minute low-priority tasks, so 5 minutes went unused. Picking a low-priority task instead would have used all 60 minutes, but then a medium task would have been skipped for a low one.

Another side effect is that when a long task doesn't fit, the scheduler keeps going, so a shorter, lower-priority task can still get in. In one of my tests, Bath (medium, 40 min) gets skipped but Brush fur (low, 10 min) still gets scheduled.

I think this is reasonable for a pet owner because getting the important tasks done matters more than filling every minute. The rules are also simple, so the plan is easy to understand and explain.

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

I wrote 6 pytest tests in tests/test_pawpal.py:

1. mark_complete() changes a task's completed value from False to True.
2. Pet.add_task() increases the number of tasks the pet has.
3. High-priority tasks come before medium and low ones in the plan. I added them in the opposite order so the scheduler actually had to sort them.
4. The plan never goes over the owner's available time, and a shorter task can still fit after a longer one is skipped.
5. Completed tasks are left out of the plan.
6. Owner.get_all_tasks() collects tasks from more than one pet, and each task has the right pet_name.

All 6 tests pass. I also ran main.py and checked the schedule by hand to make sure the order and the time left were right.

These tests are important because they cover the main things the scheduler is supposed to do: put the most important tasks first, fit in the owner's time, not repeat finished tasks, and not mix up tasks from different pets. While setting up the tests, running plain `pytest` couldn't find pawpal_system.py because the tests are in a subfolder, so I added a small pytest.ini that tells pytest to look in the project folder.

**b. Confidence**

I'm fairly confident it works for the cases I tested, since all 6 tests pass and the demo output matched what I worked out by hand. But I only have 6 tests and they use small, simple examples, so I wouldn't say it's fully proven yet.

If I had more time, I would test:

- An owner with 0 available minutes, or with no pets or tasks
- A task that uses up exactly the time that's left
- Priorities typed differently, like "High" or a typo (right now a typo gets ranked below low instead of causing an error)
- Removing a task when two tasks have the same title (remove_task only removes the first one)
- The text that explain_plan() returns

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
