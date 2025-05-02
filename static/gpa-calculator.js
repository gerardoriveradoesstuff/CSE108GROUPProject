const form = document.getElementById('gpa-form');
const courseList = document.getElementById('course-list');
const gpaResult = document.getElementById('gpa-result');

let courses = [];
let editIndex = -1;

form.addEventListener('submit', function (e) {
    e.preventDefault();

    const courseName = document.getElementById('course-name').value.trim();
    const grade = parseFloat(document.getElementById('grade').value);
    const credits = parseInt(document.getElementById('credits').value, 10);

    if (!courseName || isNaN(grade) || isNaN(credits)) return;

    const course = {courseName, grade, credits};

    if (editIndex >= 0) {
        courses[editIndex] = course;
        editIndex = -1;
    } else {
        courses.push(course);
    }

    form.reset();
    renderCourses();
    calculateGPA();
});

function renderCourses() {
    courseList.innerHTML = "";
    courses.forEach((c, index) => {
        const li = document.createElement('li');
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${c.courseName}</strong><br>
                    <small>Grade: ${c.grade} Credits: ${c.credits}</small>
                </div>
                <div class="d-flex flex-column ms-2">
                    <button class="btn btn-outline-primary btn-sm py-0 px-1 mt-4 mb-1" title="Edit" onclick="editCourse(${index})">✏️</button>
                    <button class="btn btn-outline-danger btn-sm py-0 px-1" title="Remove" onclick="deleteCourse(${index})">❌</button>
                </div>
            </div>
           `;

        courseList.appendChild(li);
    });
}

function calculateGPA() {
    let totalPoints = 0;
    let totalCredits = 0;

    for (const c of courses) {
        totalPoints += c.grade * c.credits;
        totalCredits += c.credits;
    }

    const gpa = totalCredits === 0 ? 0 : totalPoints / totalCredits;
    gpaResult.textContent = gpa.toFixed(2);
}

function deleteCourse(index) {
    courses.splice(index, 1);
    renderCourses();
    calculateGPA();
}

function editCourse(index) {
    const c = courses[index];
    document.getElementById('course-name').value = c.courseName;
    document.getElementById('grade').value = c.grade;
    document.getElementById('credits').value = c.credits;
    editIndex = index;
}

function clearAllCourses() {
    courses = [];
    editIndex = -1;
    courseList.innerHTML = "";
    calculateGPA();
}