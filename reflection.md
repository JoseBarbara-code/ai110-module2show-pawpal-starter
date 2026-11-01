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
