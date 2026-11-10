
USE school;
-- ---------------------------------------------------------------
-- Parent table: teachers (5 rows)
-- enrollment_date is used as the hire date, major as the subject area
-- ---------------------------------------------------------------
INSERT INTO teachers (teacher_id, first_name, last_name, email, phone, date_of_birth, enrollment_date, major) VALUES
(1, 'Margaret', 'Holloway', 'mholloway@school.example', '555-0101', '1975-03-14', '2010-08-20', 'Computer Science'),
(2, 'David',    'Okafor',   'dokafor@school.example',   '555-0102', '1982-11-02', '2014-01-06', 'Mathematics'),
(3, 'Elena',    'Vasquez',  'evasquez@school.example',  '555-0103', '1988-06-25', '2017-08-21', 'English'),
(4, 'Thomas',   'Brennan',  'tbrennan@school.example',  NULL,       '1970-09-09', '2008-08-18', 'Physics'),
(5, 'Priya',    'Raman',    'praman@school.example',    '555-0105', '1990-01-30', '2020-01-13', 'Business');

-- ---------------------------------------------------------------
-- Parent table: students (8 rows)
-- ---------------------------------------------------------------
INSERT INTO students (student_id, first_name, last_name, email, phone, date_of_birth, enrollment_date, major) VALUES
(1, 'Liam',    'Carter',   'liam.carter@student.example',   '555-0201', '2004-05-12', '2023-08-28', 'Software Development'),
(2, 'Sofia',   'Nguyen',   'sofia.nguyen@student.example',  '555-0202', '2003-12-01', '2023-08-28', 'Software Development'),
(3, 'Marcus',  'Bell',     'marcus.bell@student.example',   NULL,       '2005-02-17', '2024-01-08', 'Mathematics'),
(4, 'Aisha',   'Mensah',   'aisha.mensah@student.example',  '555-0204', '2004-09-03', '2024-01-08', 'Business'),
(5, 'Noah',    'Fischer',  'noah.fischer@student.example',  '555-0205', '2002-07-22', '2024-08-26', 'Physics'),
(6, 'Chloe',   'Dubois',   'chloe.dubois@student.example',  '555-0206', '2005-04-08', '2024-08-26', 'English'),
(7, 'Ethan',   'Park',     'ethan.park@student.example',    NULL,       '2003-10-15', '2025-01-13', 'Software Development'),
(8, 'Olivia',  'Santos',   'olivia.santos@student.example', '555-0208', '2004-12-19', '2025-01-13', NULL);

-- ---------------------------------------------------------------
-- Parent table: courses (6 rows)
-- ---------------------------------------------------------------
INSERT INTO courses (course_id, course_code, course_name, description, credits, instructor, max_capacity) VALUES
(1, 'CS101',   'Intro to Programming',     'Variables, control flow, functions and basic problem solving.', 3, 'Margaret Holloway', 30),
(2, 'CS210',   'Database Fundamentals',    'Relational design, SQL, normalization and joins.',              3, 'Margaret Holloway', 25),
(3, 'MATH120', 'College Algebra',          'Functions, equations, inequalities and graphs.',                4, 'David Okafor',      35),
(4, 'ENG101',  'English Composition',      'Academic writing, research and argument.',                      3, 'Elena Vasquez',     25),
(5, 'PHYS110', 'Conceptual Physics',       'Motion, energy, waves and electricity without calculus.',       4, 'Thomas Brennan',    30),
(6, 'BUS150',  'Intro to Business',        NULL,                                                            3, 'Priya Raman',       40);

-- ---------------------------------------------------------------
-- Child table: enrollments (16 rows)
-- Each (student_id, course_id) pair appears only once (primary key).
-- Completed courses have a grade; current enrollments don't yet.
-- ---------------------------------------------------------------
INSERT INTO enrollments (student_id, teacher_id, course_id, semester, enrolled_on, status, grade) VALUES
(1, 1, 1, 'Fall 2025',   '2025-08-15', 'completed', 'A'),
(1, 1, 2, 'Fall 2026',   '2026-08-12', 'enrolled',  NULL),
(1, 3, 4, 'Spring 2026', '2026-01-05', 'completed', 'B+'),
(2, 1, 1, 'Fall 2025',   '2025-08-14', 'completed', 'A-'),
(2, 1, 2, 'Fall 2026',   '2026-08-11', 'enrolled',  NULL),
(2, 2, 3, 'Spring 2026', '2026-01-06', 'completed', 'B'),
(3, 2, 3, 'Fall 2025',   '2025-08-18', 'completed', 'A'),
(3, 4, 5, 'Fall 2026',   '2026-08-13', 'enrolled',  NULL),
(4, 5, 6, 'Spring 2026', '2026-01-07', 'completed', 'A-'),
(4, 3, 4, 'Fall 2026',   '2026-08-14', 'dropped',   NULL),
(5, 4, 5, 'Spring 2026', '2026-01-05', 'completed', 'B-'),
(5, 2, 3, 'Fall 2026',   '2026-08-12', 'enrolled',  NULL),
(6, 3, 4, 'Fall 2025',   '2025-08-16', 'completed', 'A'),
(6, 5, 6, 'Fall 2026',   '2026-08-15', 'withdrawn', 'W'),
(7, 1, 1, 'Fall 2026',   '2026-08-10', 'enrolled',  NULL),
(8, 5, 6, 'Fall 2026',   '2026-08-16', 'enrolled',  NULL);