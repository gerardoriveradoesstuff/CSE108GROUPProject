# ✅ Feature 1: Sidebar Navigation
#### Why this feature?
Dashboard benefit from **persistent and global navigation** that:
- Organizes key areas like courses, grades, and profile into consistent structure
- Reduces cognitive load by letting users (students) access sections without searching. 
Giving a more naturally learned (intuitive) experience
- Matches mental models of platforms like Canvas.

#### Design rationale
We use a **left sidebar** layout because:
- most users are right-handed (and right-eye dominant), which makes vertical
navigation easier to scan on the left.
- It separates navigation from content
- Responsive frameworks (e.g. Bootstrap) support this structure well and are
quick to implement. Given the quick turnaround required for this project.


# ✅ Feature 2: Profile Summary Banner
#### Why This Feature?
A profile banner serves as a personalization anchor for the student’s dashboard. It:

This will:
- Strengthen the page header visually
- Give the student a strong contextual identity
- Begin integrating Bootstrap layout cleanly
- Helps students feel recognized (name, major, academic status)
- Summarizes key info without diving into deeper pages
- Mirrors real dashboards (Canvas, Blackboard, etc.)
- This is a top-level visual block placed above or near the dashboard greeting.

Great! Let’s move on to **Feature 3: Upcoming Deadlines Widget**.

---

# ✅ Feature 3: Upcoming Deadlines Panel

#### Why Add This?
A dashboard should answer this question at a glance:
> *“What do I need to focus on right now?”*

Adding a **Deadlines widget** gives students cues on:
- Assignments
- Projects
- Exams
- Any important due dates

This mirrors real LMS dashboards (Canvas, Blackboard, etc.), which prominently display “To Do” items.

---

#### Design Strategy

| Aspect | Choice | Reason |
|--------|--------|--------|
| **Component** | Bootstrap `card` | Consistent with profile and layout |
| **Data Structure** | List of `user.deadlines` | Iterated via Jinja |
| **Layout** | Place in right column (if later split layout), or below course tables |
| **Styling** | `list-group` | For clear, border-separated items |



---

#### Goal

Enable teachers to:
- Select a course they teach
- Enter task info and deadline date
- Save it to the database
- Let students (who are enrolled) see these deadlines on their dashboards

---

# TEACHER DASHBOARD
### Design Motivation and Layout Rationale

### Why this makes sense:
- **Teachers assign deadlines** in real life (not students).
- Students shouldn't be responsible for tracking deadlines manually — this promotes consistency and prevents confusion.

### Why we store it this way:
- **Deadlines are linked to a course and a teacher** — each deadline belongs to one course, and indirectly to its enrolled students.
- We link it to the **User (teacher)** who created it, and also store the **course_id** for student visibility.

### Why organize data this way:
- This keeps things **normalized**:
  - Courses are central
  - Teachers assign deadlines to courses
  - Students only view deadlines associated with their enrolled courses


#### `student_dashboard()` in `routes.py`


```python
from models import Deadline

@main.route("/student")
@login_required
def student_dashboard():
    user = User.query.options(
        joinedload(User.courses_enrolled).joinedload(Course.teacher)
    ).get(current_user.id)

    all_courses = Course.query.all()

    # Get all deadlines where the course is one the student is enrolled in
    course_ids = [course.id for course in user.courses_enrolled]
    deadlines = Deadline.query.filter(Deadline.course_id.in_(course_ids)).all()

    return render_template("student_dashboard.html", user=user, all_courses=all_courses, deadlines=deadlines)
```

### Why this organization?
- Keeps `User` focused on enrollment
- Deadlines are fetched via a **one-time filter** using the `course_id` values
- This pattern **separates logic**: `user.courses_enrolled` handles relationships, and `Deadline.query.filter()` does the temporal filtering

---

#### Use Deadlines in `student_dashboard.html`

```html
<div class="card mt-4 shadow-sm">
  <div class="card-header">
    📅 Upcoming Deadlines
  </div>
  <ul class="list-group list-group-flush small">
    {% if deadlines %}
      {% for deadline in deadlines %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <strong>{{ deadline.course.name }}</strong><br>
            <span class="text-muted small">{{ deadline.task }} — {{ deadline.date }}</span>
          </div>
        </li>
      {% endfor %}
    {% else %}
      <li class="list-group-item text-muted">No upcoming deadlines.</li>
    {% endif %}
  </ul>
</div>
```

> ✅ This uses the `course` relationship, so **don’t need `course_name` in the model** anymore.

---

#### Summary: Why We Built It This Way

| Design Choice | Reason |
|---------------|--------|
| `Deadline.course_id` | Enables relational filtering (students only see their course deadlines) |
| Dynamic dropdowns in admin | Prevents bad data, reflects current course/user state |
| Student view filters by `course_id` | Avoids bloated or insecure `user.deadlines` usage |
| `Deadline.course.name` in template | Uses clean, SQLAlchemy-backed relationships for readability and consistency |



----

## FRONTEND DESIGN

#### Bootstrap styling

A structure like `<h3 class="h5 mt-4 mb-2">...</h3>` (e.g. bootstrap is good for the 
DOM and application design **because it separates concerns cleanly and promotes scalable, maintainable code**. 

---

#### Why does it look like this?

It looks like this to **visually style** an `<h3>` element with the 
appearance of an `<h5>`, while keeping semantic HTML intact. 
This allows screen readers, and accessibility tools to understand the content 
hierarchy properly (`<h3>` is semantically different from `<h5>`), 
**but visually render it in a compact, styled way** using the `.h5` class.

---

#### How is the design motivated?

The design is motivated by:
- **Semantic correctness**: Keeping heading levels in logical order (`<h1>` → `<h2>` → `<h3>`, etc.)
- **Visual flexibility**: Using utility classes like `mt-4`, `mb-2`, and `h5` gives fine-grained control over margins and text appearance **without needing custom CSS**.

---

#### Why organize the data this way?

By using **utility classes** from a framework (Bootstrap), layout and spacing are:
- **Predictable** (consistent margins across elements)
- **Composable** (you can add/remove utility classes as needed)
- **Efficient** (no need to define new CSS rules for every case)

---

#### Why store it this way?

The structure stores styling *in class names*, not in inline styles or separate files. This:
- Keeps the HTML readable
- Avoids bloated CSS
- Makes it easy to adjust spacing or text size by swapping class names

---

#### Why does routing or structure matter here?

Though not directly about routing, the **hierarchical use of headings** (e.g., `<h3>`) helps build a DOM structure that’s logical for both:
- **Human readers** (visual hierarchy)
- **Machines** (assistive tech, crawlers, parsers)

If this scaled into **component or page-level routing**, the same idea applies: **structure reflects purpose** — semantic HTML for meaning, utility classes for appearance, and logical divisions (headings, sections, etc.) for flow.

---

