"""
School database website (Flask + MySQL).

Pages:
  /             Dashboard with counts
  /students     Add / list / delete students
  /teachers     Add / list / delete teachers
  /courses      Add / list / delete courses
  /enrollments  Enroll students, update status & grade, remove enrollments

Setup (once, in a terminal opened in this folder):
    py -m pip install flask mysql-connector-python

Run:
    py app.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, request, redirect, url_for, render_template, flash, abort
from jinja2 import DictLoader
import mysql.connector
from mysql.connector import Error, errorcode

# ---------------------------------------------------------------------------
# Database settings: change the password (and database name if needed)
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Pass1234",
    "database": "school",
}

app = Flask(__name__)
app.secret_key = "change-me"  # needed for flash messages


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def query(sql, params=(), one=False):
    """Run a SELECT and return rows as dictionaries."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        return rows[0] if one and rows else (None if one else rows)
    finally:
        conn.close()


def execute(sql, params=()):
    """Run an INSERT / UPDATE / DELETE and commit it."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def friendly_error(e):
    """Turn common MySQL errors into readable messages."""
    if e.errno == errorcode.ER_DUP_ENTRY:
        return "That record already exists (a unique value such as an email or course code is already in use)."
    if e.errno == errorcode.ER_ROW_IS_REFERENCED_2:
        return "This record can't be deleted because it is used by one or more enrollments. Remove those enrollments first."
    if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
        return "The selected student, teacher or course doesn't exist."
    if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        return "MySQL rejected the username or password. Check DB_CONFIG in app.py."
    if e.errno == errorcode.ER_BAD_DB_ERROR:
        return "The database doesn't exist. Run your CREATE DATABASE script in Workbench first."
    if e.errno == 2003:
        return "Can't reach MySQL. Make sure the MySQL84 service is running (services.msc)."
    return f"Database error: {e}"


# ---------------------------------------------------------------------------
# Table definitions for the three simple tables.
# Each field: (column, label, input type, required?)
# Optional fields left blank become NULL. Fields marked "default" are left
# out of the INSERT when blank, so MySQL's DEFAULT value is used instead.
# ---------------------------------------------------------------------------
PERSON_FIELDS = [
    ("first_name", "First name", "text", True),
    ("last_name", "Last name", "text", True),
    ("email", "Email", "email", True),
    ("phone", "Phone", "tel", False),
    ("date_of_birth", "Date of birth", "date", False),
    ("enrollment_date", "Enrollment date (blank = today)", "date", "default"),
    ("major", "Major", "text", False),
]

TABLES = {
    "students": {
        "title": "Students",
        "singular": "student",
        "pk": "student_id",
        "fields": PERSON_FIELDS,
        "columns": [("student_id", "ID"), ("first_name", "First"), ("last_name", "Last"),
                    ("email", "Email"), ("phone", "Phone"), ("date_of_birth", "Born"),
                    ("enrollment_date", "Enrolled"), ("major", "Major")],
        "order": "last_name, first_name",
    },
    "teachers": {
        "title": "Teachers",
        "singular": "teacher",
        "pk": "teacher_id",
        "fields": PERSON_FIELDS,
        "columns": [("teacher_id", "ID"), ("first_name", "First"), ("last_name", "Last"),
                    ("email", "Email"), ("phone", "Phone"), ("date_of_birth", "Born"),
                    ("enrollment_date", "Start date"), ("major", "Major")],
        "order": "last_name, first_name",
    },
    "courses": {
        "title": "Courses",
        "singular": "course",
        "pk": "course_id",
        "fields": [
            ("course_code", "Course code (e.g. CS101)", "text", True),
            ("course_name", "Course name", "text", True),
            ("description", "Description", "textarea", False),
            ("credits", "Credits (blank = 3)", "number", "default"),
            ("instructor", "Instructor", "text", False),
            ("max_capacity", "Max capacity (blank = 30)", "number", "default"),
        ],
        "columns": [("course_id", "ID"), ("course_code", "Code"), ("course_name", "Name"),
                    ("credits", "Credits"), ("instructor", "Instructor"),
                    ("max_capacity", "Capacity")],
        "order": "course_code",
    },
}

# Maximum lengths, matching the VARCHAR sizes in the schema
MAXLEN = {"first_name": 50, "last_name": 50, "email": 100, "phone": 20, "major": 100,
          "course_code": 10, "course_name": 100, "instructor": 100, "semester": 20}

STATUSES = ["enrolled", "completed", "dropped", "withdrawn"]


# ---------------------------------------------------------------------------
# Routes: dashboard
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    counts = {}
    try:
        for t in ("students", "teachers", "courses", "enrollments"):
            counts[t] = query(f"SELECT COUNT(*) AS n FROM {t}", one=True)["n"]
    except Error as e:
        flash(friendly_error(e), "err")
    return render_template("index.html", counts=counts)


# ---------------------------------------------------------------------------
# Routes: students / teachers / courses (shared code)
# ---------------------------------------------------------------------------
@app.route("/<table>", methods=["GET", "POST"])
def manage(table):
    if table not in TABLES:
        abort(404)
    cfg = TABLES[table]

    if request.method == "POST":
        cols, values = [], []
        for name, _label, _type, required in cfg["fields"]:
            value = request.form.get(name, "").strip()
            if value == "":
                if required is True:
                    flash(f"{_label} is required.", "err")
                    return redirect(url_for("manage", table=table))
                if required == "default":
                    continue  # let MySQL use its DEFAULT
                value = None
            cols.append(name)
            values.append(value)
        placeholders = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        try:
            execute(sql, values)
            flash(f"{cfg['singular'].capitalize()} added.", "ok")
        except Error as e:
            flash(friendly_error(e), "err")
        return redirect(url_for("manage", table=table))

    rows = []
    try:
        rows = query(f"SELECT * FROM {table} ORDER BY {cfg['order']}")
    except Error as e:
        flash(friendly_error(e), "err")
    return render_template("table.html", table=table, cfg=cfg, rows=rows, maxlen=MAXLEN)


@app.route("/<table>/<int:row_id>/delete", methods=["POST"])
def delete_row(table, row_id):
    if table not in TABLES:
        abort(404)
    cfg = TABLES[table]
    try:
        execute(f"DELETE FROM {table} WHERE {cfg['pk']} = %s", (row_id,))
        flash(f"{cfg['singular'].capitalize()} deleted.", "ok")
    except Error as e:
        flash(friendly_error(e), "err")
    return redirect(url_for("manage", table=table))


# ---------------------------------------------------------------------------
# Routes: enrollments
# ---------------------------------------------------------------------------
@app.route("/enrollments", methods=["GET", "POST"])
def enrollments():
    if request.method == "POST":
        f = request.form
        student_id, teacher_id, course_id = f.get("student_id"), f.get("teacher_id"), f.get("course_id")
        semester = f.get("semester", "").strip()
        status = f.get("status", "enrolled")
        grade = f.get("grade", "").strip().upper() or None

        if not (student_id and teacher_id and course_id and semester):
            flash("Student, teacher, course and semester are all required.", "err")
            return redirect(url_for("enrollments"))
        if status not in STATUSES:
            status = "enrolled"

        try:
            # The primary key (student_id, course_id) allows one enrollment per student per course
            if query("SELECT 1 FROM enrollments WHERE student_id = %s AND course_id = %s",
                     (student_id, course_id), one=True):
                flash("That student is already enrolled in that course.", "err")
                return redirect(url_for("enrollments"))

            # Respect the course's max_capacity
            course = query("SELECT course_code, max_capacity FROM courses WHERE course_id = %s",
                           (course_id,), one=True)
            taken = query("SELECT COUNT(*) AS n FROM enrollments "
                          "WHERE course_id = %s AND status = 'enrolled'", (course_id,), one=True)["n"]
            if course and status == "enrolled" and taken >= course["max_capacity"]:
                flash(f"{course['course_code']} is full ({course['max_capacity']} students).", "err")
                return redirect(url_for("enrollments"))

            execute("INSERT INTO enrollments (student_id, teacher_id, course_id, semester, status, grade) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (student_id, teacher_id, course_id, semester, status, grade))
            flash("Enrollment added.", "ok")
        except Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                flash("That student is already enrolled in that course.", "err")
            else:
                flash(friendly_error(e), "err")
        return redirect(url_for("enrollments"))

    rows, students, teachers, courses = [], [], [], []
    try:
        rows = query("""
            SELECT e.student_id, e.course_id, e.semester, e.enrolled_on, e.status, e.grade,
                   CONCAT(s.first_name, ' ', s.last_name) AS student,
                   CONCAT(t.first_name, ' ', t.last_name) AS teacher,
                   c.course_code, c.course_name
            FROM enrollments e
            JOIN students s ON s.student_id = e.student_id
            JOIN teachers t ON t.teacher_id = e.teacher_id
            JOIN courses  c ON c.course_id  = e.course_id
            ORDER BY e.semester, c.course_code, s.last_name
        """)
        students = query("SELECT student_id, first_name, last_name FROM students ORDER BY last_name, first_name")
        teachers = query("SELECT teacher_id, first_name, last_name FROM teachers ORDER BY last_name, first_name")
        courses = query("SELECT course_id, course_code, course_name FROM courses ORDER BY course_code")
    except Error as e:
        flash(friendly_error(e), "err")
    return render_template("enrollments.html", rows=rows, students=students,
                           teachers=teachers, courses=courses, statuses=STATUSES)


@app.route("/enrollments/<int:student_id>/<int:course_id>/update", methods=["POST"])
def update_enrollment(student_id, course_id):
    status = request.form.get("status")
    grade = request.form.get("grade", "").strip().upper() or None
    if status not in STATUSES:
        flash("Invalid status.", "err")
        return redirect(url_for("enrollments"))
    try:
        execute("UPDATE enrollments SET status = %s, grade = %s "
                "WHERE student_id = %s AND course_id = %s",
                (status, grade, student_id, course_id))
        flash("Enrollment updated.", "ok")
    except Error as e:
        flash(friendly_error(e), "err")
    return redirect(url_for("enrollments"))


@app.route("/enrollments/<int:student_id>/<int:course_id>/delete", methods=["POST"])
def delete_enrollment(student_id, course_id):
    try:
        execute("DELETE FROM enrollments WHERE student_id = %s AND course_id = %s",
                (student_id, course_id))
        flash("Enrollment removed.", "ok")
    except Error as e:
        flash(friendly_error(e), "err")
    return redirect(url_for("enrollments"))


# ---------------------------------------------------------------------------
# HTML templates (kept in this file so there's only one file to run)
# ---------------------------------------------------------------------------
TEMPLATES = {
"base.html": """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}School{% endblock %} · School DB</title>
  <style>
    :root { --bg:#f6f7f9; --card:#fff; --ink:#1d2330; --muted:#667085; --line:#e3e6eb;
            --accent:#2f5bd3; --ok:#e5f5ea; --okink:#1c6b35; --err:#fdeaea; --errink:#9b1c1c; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: system-ui, "Segoe UI", sans-serif; background:var(--bg); color:var(--ink); }
    nav { background:var(--ink); padding:0 24px; display:flex; gap:4px; flex-wrap:wrap; }
    nav a { color:#cfd5e1; text-decoration:none; padding:14px 12px; font-size:15px; }
    nav a.brand { color:#fff; font-weight:600; margin-right:12px; }
    nav a.active, nav a:hover { color:#fff; background:rgba(255,255,255,.08); }
    main { max-width:1100px; margin:28px auto; padding:0 20px; }
    h1 { margin:0 0 20px; font-size:26px; }
    h2 { font-size:18px; margin:0 0 14px; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:20px; margin-bottom:24px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px,1fr)); gap:14px; }
    label { display:flex; flex-direction:column; gap:5px; font-size:13px; color:var(--muted); }
    label.wide { grid-column:1 / -1; }
    input, select, textarea { font:inherit; font-size:15px; color:var(--ink); padding:8px 10px;
            border:1px solid var(--line); border-radius:6px; background:#fff; }
    textarea { min-height:70px; resize:vertical; }
    button { font:inherit; font-size:15px; padding:9px 18px; border:0; border-radius:6px;
             background:var(--accent); color:#fff; cursor:pointer; }
    button.small { font-size:13px; padding:5px 10px; }
    button.danger { background:transparent; color:var(--errink); border:1px solid #f0c4c4; }
    .actions { margin-top:16px; }
    .table-wrap { overflow-x:auto; }
    table { border-collapse:collapse; width:100%; font-size:14px; }
    th, td { text-align:left; padding:9px 10px; border-bottom:1px solid var(--line); white-space:nowrap; }
    th { color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }
    td form { display:inline; margin:0; }
    td.inline-edit form { display:flex; gap:6px; align-items:center; }
    td.inline-edit select, td.inline-edit input { padding:4px 6px; font-size:13px; }
    .msg { padding:11px 14px; border-radius:6px; margin-bottom:16px; }
    .ok { background:var(--ok); color:var(--okink); }
    .err { background:var(--err); color:var(--errink); }
    .empty { color:var(--muted); }
    .stats { display:grid; grid-template-columns:repeat(auto-fill, minmax(200px,1fr)); gap:14px; }
    .stat { display:block; text-decoration:none; color:inherit; }
    .stat .n { font-size:34px; font-weight:700; }
    .stat .l { color:var(--muted); }
    .badge { padding:2px 8px; border-radius:20px; font-size:12px; background:#eef1f6; }
    .badge.enrolled { background:#e7eefc; color:#24479f; }
    .badge.completed { background:var(--ok); color:var(--okink); }
    .badge.dropped, .badge.withdrawn { background:#f3f0e8; color:#7a5b12; }
  </style>
</head>
<body>
  <nav>
    <a class="brand" href="{{ url_for('index') }}">School DB</a>
    {% set here = request.path %}
    <a href="{{ url_for('manage', table='students') }}" class="{{ 'active' if here.startswith('/students') }}">Students</a>
    <a href="{{ url_for('manage', table='teachers') }}" class="{{ 'active' if here.startswith('/teachers') }}">Teachers</a>
    <a href="{{ url_for('manage', table='courses') }}" class="{{ 'active' if here.startswith('/courses') }}">Courses</a>
    <a href="{{ url_for('enrollments') }}" class="{{ 'active' if here.startswith('/enrollments') }}">Enrollments</a>
  </nav>
  <main>
    {% for category, message in get_flashed_messages(with_categories=true) %}
      <div class="msg {{ category }}">{{ message }}</div>
    {% endfor %}
    {% block content %}{% endblock %}
  </main>
</body>
</html>""",

"index.html": """{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<h1>Dashboard</h1>
<div class="stats">
  {% for key, label, endpoint in [("students","Students","students"), ("teachers","Teachers","teachers"),
                                   ("courses","Courses","courses"), ("enrollments","Enrollments","enrollments")] %}
  <a class="card stat" href="{{ url_for('enrollments') if key == 'enrollments' else url_for('manage', table=key) }}">
    <div class="n">{{ counts.get(key, '–') }}</div><div class="l">{{ label }}</div>
  </a>
  {% endfor %}
</div>
{% endblock %}""",

"table.html": """{% extends "base.html" %}
{% block title %}{{ cfg.title }}{% endblock %}
{% block content %}
<h1>{{ cfg.title }}</h1>

<div class="card">
  <h2>Add a {{ cfg.singular }}</h2>
  <form method="post">
    <div class="grid">
    {% for name, label, type, required in cfg.fields %}
      <label class="{{ 'wide' if type == 'textarea' }}">{{ label }}{% if required == true %} *{% endif %}
        {% if type == 'textarea' %}
          <textarea name="{{ name }}"></textarea>
        {% else %}
          <input name="{{ name }}" type="{{ type }}"
                 {% if maxlen.get(name) %}maxlength="{{ maxlen[name] }}"{% endif %}
                 {% if type == 'number' %}min="0"{% endif %}
                 {% if required == true %}required{% endif %}>
        {% endif %}
      </label>
    {% endfor %}
    </div>
    <div class="actions"><button type="submit">Add {{ cfg.singular }}</button></div>
  </form>
</div>

<div class="card">
  <h2>All {{ cfg.title | lower }} ({{ rows | length }})</h2>
  {% if rows %}
  <div class="table-wrap">
  <table>
    <tr>{% for col, label in cfg.columns %}<th>{{ label }}</th>{% endfor %}<th></th></tr>
    {% for r in rows %}
    <tr>
      {% for col, label in cfg.columns %}<td>{{ r[col] if r[col] is not none else '' }}</td>{% endfor %}
      <td>
        <form method="post" action="{{ url_for('delete_row', table=table, row_id=r[cfg.pk]) }}"
              onsubmit="return confirm('Delete this {{ cfg.singular }}?');">
          <button class="small danger">Delete</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
  </div>
  {% else %}
  <p class="empty">No {{ cfg.title | lower }} yet.</p>
  {% endif %}
</div>
{% endblock %}""",

"enrollments.html": """{% extends "base.html" %}
{% block title %}Enrollments{% endblock %}
{% block content %}
<h1>Enrollments</h1>

<div class="card">
  <h2>Enroll a student</h2>
  {% if students and teachers and courses %}
  <form method="post">
    <div class="grid">
      <label>Student *
        <select name="student_id" required>
          <option value="">Choose…</option>
          {% for s in students %}<option value="{{ s.student_id }}">{{ s.last_name }}, {{ s.first_name }}</option>{% endfor %}
        </select>
      </label>
      <label>Course *
        <select name="course_id" required>
          <option value="">Choose…</option>
          {% for c in courses %}<option value="{{ c.course_id }}">{{ c.course_code }} – {{ c.course_name }}</option>{% endfor %}
        </select>
      </label>
      <label>Teacher *
        <select name="teacher_id" required>
          <option value="">Choose…</option>
          {% for t in teachers %}<option value="{{ t.teacher_id }}">{{ t.last_name }}, {{ t.first_name }}</option>{% endfor %}
        </select>
      </label>
      <label>Semester *
        <input name="semester" placeholder="e.g. Fall 2026" maxlength="20" required>
      </label>
      <label>Status
        <select name="status">{% for st in statuses %}<option>{{ st }}</option>{% endfor %}</select>
      </label>
      <label>Grade
        <input name="grade" maxlength="2" placeholder="e.g. A-">
      </label>
    </div>
    <div class="actions"><button type="submit">Add enrollment</button></div>
  </form>
  {% else %}
  <p class="empty">Add at least one student, one teacher and one course before creating enrollments.</p>
  {% endif %}
</div>

<div class="card">
  <h2>All enrollments ({{ rows | length }})</h2>
  {% if rows %}
  <div class="table-wrap">
  <table>
    <tr><th>Semester</th><th>Course</th><th>Student</th><th>Teacher</th><th>Enrolled on</th>
        <th>Status</th><th>Status / grade</th><th></th></tr>
    {% for r in rows %}
    <tr>
      <td>{{ r.semester }}</td>
      <td>{{ r.course_code }} – {{ r.course_name }}</td>
      <td>{{ r.student }}</td>
      <td>{{ r.teacher }}</td>
      <td>{{ r.enrolled_on }}</td>
      <td><span class="badge {{ r.status }}">{{ r.status }}</span></td>
      <td class="inline-edit">
        <form method="post" action="{{ url_for('update_enrollment', student_id=r.student_id, course_id=r.course_id) }}">
          <select name="status">
            {% for st in statuses %}<option {{ 'selected' if st == r.status }}>{{ st }}</option>{% endfor %}
          </select>
          <input name="grade" value="{{ r.grade or '' }}" maxlength="2" size="3" placeholder="—">
          <button class="small">Save</button>
        </form>
      </td>
      <td>
        <form method="post" action="{{ url_for('delete_enrollment', student_id=r.student_id, course_id=r.course_id) }}"
              onsubmit="return confirm('Remove this enrollment?');">
          <button class="small danger">Remove</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
  </div>
  {% else %}
  <p class="empty">No enrollments yet.</p>
  {% endif %}
</div>
{% endblock %}""",
}

app.jinja_loader = DictLoader(TEMPLATES)


if __name__ == "__main__":
    app.run(debug=True)
