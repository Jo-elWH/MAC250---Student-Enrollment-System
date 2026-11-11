DROP DATABASE school;
create database school;
use school;

CREATE TABLE teachers (
    teacher_id      INT UNSIGNED    NOT NULL AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    UNIQUE NOT NULL,
    phone           VARCHAR(20)     NULL,
    date_of_birth   DATE            NULL,
    enrollment_date DATE            NOT NULL DEFAULT (CURRENT_DATE),
    major           VARCHAR(100)    NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    student_id      INT UNSIGNED    NOT NULL AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    UNIQUE NOT NULL,
    phone           VARCHAR(20)     NULL,
    date_of_birth   DATE            NULL,
    enrollment_date DATE            NOT NULL DEFAULT (CURRENT_DATE),
    major           VARCHAR(100)    NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    course_id       INT UNSIGNED      NOT NULL AUTO_INCREMENT PRIMARY KEY,
    course_code     VARCHAR(10)       NOT NULL UNIQUE,
    course_name     VARCHAR(100)      NOT NULL,
    description     TEXT              NULL,
    credits         TINYINT UNSIGNED  NOT NULL DEFAULT 3,
    instructor      VARCHAR(100)      NULL,
    max_capacity    SMALLINT UNSIGNED NOT NULL DEFAULT 30,
    created_at      TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enrollments (
    student_id      INT UNSIGNED    NOT NULL,
    teacher_id      INT UNSIGNED    NOT NULL,
    course_id       INT UNSIGNED    NOT NULL,
    semester        VARCHAR(20)     NOT NULL,         
    enrolled_on     DATE            NOT NULL DEFAULT (CURRENT_DATE),
    status          ENUM('enrolled', 'completed', 'dropped', 'withdrawn')
                                    NOT NULL DEFAULT 'enrolled',
    grade           VARCHAR(2)      NULL,              
   PRIMARY KEY (student_id, course_id),
   FOREIGN KEY (student_id) REFERENCES students (student_id),
   FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id),
   FOREIGN KEY (course_id) REFERENCES courses (course_id)
        
);
