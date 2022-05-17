USE university;
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS users;
CREATE TABLE users(
  user_id      int(8) PRIMARY KEY not null,
  username     varchar(50)        not null,
  password     varchar(50)        not null,
  utype        varchar(50)        not null,
  fname        char(50)           not null,          
  lname        char(50)           not null,
  pronouns     varchar(50),                
  dob          varchar(10),    
  phone        varchar(50),     
  email        varchar(50),        
  street_add   varchar(50),       
  city         varchar(50),        
  state        char(2),           
  zipcode      int(5),
  ssn          int(8)            
);

DROP TABLE IF EXISTS students;
CREATE TABLE students(
    s_id    INTEGER(8) PRIMARY KEY not null,
    program  varchar(3) not null,
    thesis  varchar(1000),
    approved varchar(3),
    foreign key (s_id) references users(user_id)

);

DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni(
    alumni_id    INTEGER(8) PRIMARY KEY not null,
    program      varchar(3) ,
    grad_yr      varchar(4),
    foreign key (alumni_id) references users(user_id)

);

-- APPS specific tables
DROP TABLE IF EXISTS applications;
CREATE TABLE applications(
  app_id       int(8) PRIMARY KEY not null,
  deg_sought   char(3)            not null,
  area_of_int  varchar(50)        not null,
  work_exp     varchar(50)        not null,
  app_sem      char(6)            not null,
  app_year     int(4)             not null,
  transcript   char(1),
  app_stat     char(50)           not null,
  decision     char(50),
  foreign key (app_id) references users(user_id)
);

DROP TABLE IF EXISTS degrees;
CREATE TABLE degrees(
  deg_id       varchar(5)          not null,
  app_id       int(8)              not null,
  deg_year     varchar(4)          not null,
  uni          varchar(50)         not null,
  gpa          float(3, 2)         not null,
  major        varchar(50)         not null,
  PRIMARY KEY (deg_id, app_id),
  foreign key (app_id) references users(user_id)
);

DROP TABLE IF EXISTS tests;
CREATE TABLE tests(
  app_id       int(8) PRIMARY KEY not null,
  gre_score    int(3)             not null,
  gre_v        int(3)             not null,
  gre_q        int(3)             not null,
  gre_year     int(4)             not null,
  gre_sub      varchar(50),
  toefl        int(3),
  toefl_date   varchar(10),
  foreign key (app_id) references users(user_id)
);

DROP TABLE IF EXISTS rec_letters;
CREATE TABLE rec_letters(
  rec_id       int(5) not null AUTO_INCREMENT PRIMARY KEY,
  app_id       int(8) not null,
  wname        varchar(50) not null,
  wemail       varchar(50) not null,
  wtitle       varchar(50) not null,
  date         date not null,
  letter       varchar(3500),
  rating       int(1),
  generic      char(1),
  credibility  char(1),
  foreign key (app_id) references users(user_id)
);
 ALTER TABLE rec_letters AUTO_INCREMENT = 10000;

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews(
  rev_id       int(8) not null,
  app_id       int(8) not null,
  gas_rev      varchar(50)        not null,
  course_def   varchar(50),
  comments     varchar(50),
  final_dec    varchar(50)        not null,
  reason       varchar(1)         not null,
  rec_advisor  varchar(50), 
  PRIMARY KEY (rev_id, app_id),
  foreign key (app_id) references users(user_id)
);


INSERT INTO users VALUES (10000003, 'facrev', 'fr_pass', 'fac_rev', 'Fac', 'Rev', 'he/him', '2003-03-03', '123-345-4567', 'fa@email.com', '345 C St.', 'Chicago', 'IL', 60007, null);


-- REGS specific tables
DROP TABLE IF EXISTS constants;
CREATE TABLE constants(
  cur_year     char(4)            not null,
  cur_sem      char(6)            not null
);

DROP TABLE IF EXISTS enrolled_in;
CREATE TABLE enrolled_in(
  student_id   int(8)             not null,
  course_id    int(2)             not null,
  semester     char(6)            not null,
  year         char(4)             not null,
  grade        varchar(2)         not null,
  PRIMARY KEY (student_id, course_id)
);

DROP TABLE IF EXISTS courses;
CREATE TABLE courses(
  course_id    int(8) PRIMARY KEY not null,
  dept         char(50)           not null,
  cnum         int(4)             not null,
  title        varchar(50)        not null,
  credits      int(1)             not null
);

DROP TABLE IF EXISTS prereq_of;
CREATE TABLE prereq_of(
  course_id    int(2)             not null,
  pr_cid       int(2)             not null
);

DROP TABLE IF EXISTS courses_offered;
CREATE TABLE courses_offered(
  course_id    int(2) PRIMARY KEY not null,
  day          char(50)           not null,
  start_time   int(4)             not null,
  end_time     int(1)             not null
);

DROP TABLE IF EXISTS teaches;
CREATE TABLE teaches(
  faculty_id   char(50)           not null,
  course_id    int(2) PRIMARY KEY not null,
  semester     char(6)            not null,
  year         char(4)               not null
);

DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty(
  faculty_id    int(2)             not null,
  faculty_type  int(2)             not null
);

-- ADS specifc tables

DROP TABLE IF EXISTS forms;
CREATE TABLE forms(
  faculty_id    int(2)             not null,
  faculty_type  int(2)             not null
);

DROP TABLE IF EXISTS advises;
CREATE TABLE advises(
  s_id          int(8)  PRIMARY KEY not null,
  adv_id        int(8)             not null
);

DROP TABLE IF EXISTS applies;
CREATE TABLE applies(
  s_id          int(8) PRIMARY KEY not null,
  gpa           float(3, 2)        not null,       
  credits       int(2)             not null         
);

DROP TABLE IF EXISTS form_one;
CREATE TABLE form_one(
    s_id   INTEGER(8) not null,
    course_id   integer(8) not null,
    foreign key (s_id) references students(s_id),
    foreign key (course_id) references courses(course_id)
);
SET FOREIGN_KEY_CHECKS=1;



-- ----------------------------------------------------------------------------------
-- REGS TEST DATA
-- -----------------------------------------------------------------------------------


INSERT INTO constants VALUES ('2022', 'SPRING');

INSERT INTO courses VALUES (0001, 'CSCI', 6221, 'SW Paradigms', 3);
INSERT INTO courses VALUES (0002, 'CSCI', 6461, 'Computer Architecture', 3);
INSERT INTO courses VALUES (0003, 'CSCI', 6212, 'Algorithms', 3);
INSERT INTO courses VALUES (0004, 'CSCI', 6220, 'Machine Learning', 3);
INSERT INTO courses VALUES (0005, 'CSCI', 6232, 'Networks 1', 3);
INSERT INTO courses VALUES (0006, 'CSCI', 6233, 'Networks 2', 3);
INSERT INTO courses VALUES (0007, 'CSCI', 6241, 'Database 1', 3);
INSERT INTO courses VALUES (0008, 'CSCI', 6242, 'Database 2', 3);
INSERT INTO courses VALUES (0009, 'CSCI', 6246, 'Compilers', 3);
INSERT INTO courses VALUES (0010, 'CSCI', 6260, 'Multimedia', 3);
INSERT INTO courses VALUES (0011, 'CSCI', 6251, 'Cloud Computing', 3);
INSERT INTO courses VALUES (0012, 'CSCI', 6254, 'SW Engineering', 3);
INSERT INTO courses VALUES (0013, 'CSCI', 6262, 'Graphics 1', 3);
INSERT INTO courses VALUES (0014, 'CSCI', 6283, 'Security 1', 3);
INSERT INTO courses VALUES (0015, 'CSCI', 6284, 'Cryptography', 3);
INSERT INTO courses VALUES (0016, 'CSCI', 6286, 'Network Security', 3);
INSERT INTO courses VALUES (0017, 'CSCI', 6325, 'Algorithms 2', 3);
INSERT INTO courses VALUES (0018, 'CSCI', 6339, 'Embedded Systems', 3);
INSERT INTO courses VALUES (0019, 'CSCI', 6384, 'Cryptography 2', 3);
INSERT INTO courses VALUES (0020, 'ECE', 6241, 'Communication Theory', 3);
INSERT INTO courses VALUES (0021, 'ECE', 6242, 'Information Theory', 2);
INSERT INTO courses VALUES (0022, 'MATH', 6210, 'Logic', 2);


INSERT INTO prereq_of VALUES (0006, 0005);
INSERT INTO prereq_of VALUES (0008, 0007);
INSERT INTO prereq_of VALUES (0009, 0002);
INSERT INTO prereq_of VALUES (0009, 0003);
INSERT INTO prereq_of VALUES (0011, 0002);
INSERT INTO prereq_of VALUES (0014, 0003);
INSERT INTO prereq_of VALUES (0015, 0003);
INSERT INTO prereq_of VALUES (0016, 0014);
INSERT INTO prereq_of VALUES (0016, 0005);
INSERT INTO prereq_of VALUES (0017, 0003);
INSERT INTO prereq_of VALUES (0018, 0002);
INSERT INTO prereq_of VALUES (0018, 0003);
INSERT INTO prereq_of VALUES (0019, 0015);

INSERT INTO courses_offered VALUES (0001, 'M', 1500, 1730);
INSERT INTO courses_offered VALUES (0002, 'T', 1500, 1730);
INSERT INTO courses_offered VALUES (0003, 'W', 1500, 1730);
INSERT INTO courses_offered VALUES (0005, 'M', 1800, 2030);
INSERT INTO courses_offered VALUES (0006, 'T', 1800, 2030);
INSERT INTO courses_offered VALUES (0007, 'W', 1800, 2030);
INSERT INTO courses_offered VALUES (0008, 'R', 1800, 2030);
INSERT INTO courses_offered VALUES (0009, 'T', 1500, 1730);
INSERT INTO courses_offered VALUES (0011, 'M', 1800, 2030);
INSERT INTO courses_offered VALUES (0010, 'R', 1800, 2030);
INSERT INTO courses_offered VALUES (0013, 'W', 1800, 2030);
INSERT INTO courses_offered VALUES (0014, 'T', 1800, 2030);
INSERT INTO courses_offered VALUES (0015, 'M', 1800, 2030);
INSERT INTO courses_offered VALUES (0016, 'W', 1800, 2030);
INSERT INTO courses_offered VALUES (0019, 'W', 1500, 1730);
INSERT INTO courses_offered VALUES (0020, 'M', 1800, 2030);
INSERT INTO courses_offered VALUES (0021, 'T', 1800, 2030);
INSERT INTO courses_offered VALUES (0022, 'W', 1800, 2030);
INSERT INTO courses_offered VALUES (0018, 'R', 1600, 1830);

INSERT INTO users VALUES (10000014, 'bholiday', 'holiday', 'student', 'Billie', 'Holiday', null, null, null, 'bholiday@school.edu', '123 Main St', null, null, null, null);
INSERT INTO users VALUES (10000015, 'dkrall', 'krall', 'student', 'Diana', 'Krall', null, null, null, 'dkrall@school.edu', '456 Main St', null, null, null, null);
INSERT INTO students VALUES (10000014, 'MS', null, null);
INSERT INTO students VALUES (10000015, 'MS', null, null);

INSERT INTO enrolled_in VALUES (10000014, 0002, 'Spring', 2022, 'IP');
INSERT INTO enrolled_in VALUES (10000015, 0002, 'Spring', 2022, 'IP');
INSERT INTO enrolled_in VALUES (10000014, 0003, 'Spring', 2022, 'IP');

INSERT INTO users VALUES (10000012, 'bnarahari', 'narahari', 'Instructor', 'Bhagirath', 'Narahari', null, null, null, 'bhagi@school.com', '789 Main St', null, null, null, null);
INSERT INTO users VALUES (10000013, 'hchoi', 'choi', 'Instructor', 'Hyeong-Ah', 'Choi', null, null, null, 'hchoi@school.com', '101 Main St', null, null, null, null);

INSERT INTO users VALUES (10000002, 'gradsec', 'gs_pass', 'grad_sec', 'Grad', 'Sec', 'she/her', '2002-02-02', '123-234-3456', 'gs@email.com', '234 B St.', 'Philadelphia', 'PA', 19019, null);
INSERT INTO users VALUES (10000001, 'sysadmin', 'sys_pass', 'sys_admin', 'Sys', 'Admin', 'they/them', '2001-01-01', '123-456-7890', 'sysadmin@email.com', '123 A St.', 'Washington', 'DC', 20052, null);

INSERT INTO teaches VALUES (10000012, 0002, 'Spring', '2022');
INSERT INTO teaches VALUES (10000013, 0003, 'Spring', '2022');

-- -----------------------------------------------------------------------------------------
-- APPS TEST DATA
-- -----------------------------------------------------------------------------------------
-- application is complete but no reviews.
INSERT INTO users VALUES (10000010, 'johnl', 'johnlpass', 'applicant', 'John', 'Lennon', 'he/him', '1940-10-09', '914-906-7855', 'johnl@email.com', '400 F St.', 'Sterling', 'VA', 20163, 111111111);
-- application is incomplete
INSERT INTO users VALUES (10000017, 'ringos', 'rspass', 'applicant', 'Ringo', 'Starr', 'he/him', '1940-07-07', '310-859-9688', 'ringos@email.com', '500 E St.', 'New York', 'NY', 10001, 222111111);

INSERT INTO applications VALUES (10000010, 'PHD', 'Music', 'Spent 65 years in the field.', 'Spring', 2023, 'Y', 'COMPLETE', 'NA');
INSERT INTO applications VALUES (10000017, 'MS', 'Percussion', 'Had an internship once.', 'Fall', 2022, 'N', 'INCOMPLETE', 'NA');

INSERT INTO users VALUES (10000004, 'cac', 'cac_pass', 'cac', 'Ca', 'C', 'they/them', '2004-04-04', '123-456-5678', 'cac@email.com', '456 D St.', 'Boulder', 'CO', 80301, null);

 INSERT INTO users VALUES (27777773, 'narahari_rev', 'bpass', 'fac_rev', 'Bhagi', 'Narahari', null, null, null, null, null, null, null, null, null);

INSERT INTO users VALUES (27777778, 'twood', 'tpass', 'fac_rev', 'Tim', 'Wood', null, null, null, null, null, null, null, null, null);

INSERT INTO users VALUES (27777779, 'sheller', 'spass', 'fac_rev', 'Shelly', 'Heller', null, null, null, null, null, null, null, null, null);

-- -----------------------------------------------------------------------------------------
-- ADS TEST DATA
-- -----------------------------------------------------------------------------------------
-- Has registered for and completed CSCI 6221,6212,6461,6232,6233 with all A’s. Has registered and completed CSCI6241, 6246, 6262, 6283, 6242 with all B’s.
INSERT INTO users VALUES (55555555, 'paulm', 'pass', 'student', 'Paul', 'McCartney', null, null, null, null, null, null, null, null, null);
INSERT INTO students VALUES (55555555, 'MS', null, null);
INSERT INTO enrolled_in VALUES (55555555, 0001, 'Fall', '2021', 'A');
INSERT INTO enrolled_in VALUES (55555555, 0003,  'Fall', '2021', 'A');
INSERT INTO enrolled_in VALUES (55555555, 0002,  'Fall', '2021', 'A');
INSERT INTO enrolled_in VALUES (55555555, 0005,  'Fall', '2021', 'A');
INSERT INTO enrolled_in VALUES (55555555, 0006,  'Fall', '2021', 'A');
INSERT INTO enrolled_in VALUES (55555555, 0007,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (55555555, 0009,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (55555555, 0013,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (55555555, 0014,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (55555555, 0008,  'Spring', '2022', 'B');
-- has registered for and completed ECE6242 with a C grade, and CSCI 6221, 6461,6212, 6232, 6233, 6241,6242, 6283, 6284 with all B’s on the CSCI courses.
INSERT INTO users VALUES (66666666, 'georgeh', 'pass', 'student', 'George', 'Harrison', null, null, null, null, null, null, null, null, null);
INSERT INTO students VALUES (66666666, 'MS', null, null);
INSERT INTO enrolled_in VALUES (66666666, 0001, 'Fall', '2021', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0003,  'Fall', '2021', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0002,  'Fall', '2021', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0005,  'Spring', '2024', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0006,  'Spring', '2023', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0015,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0009,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0013,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0014,  'Spring', '2022', 'B');
INSERT INTO enrolled_in VALUES (66666666, 0021,  'Spring', '2022', 'C');
-- completed 12 CS classes with all As. The advisor should not yet have approved their thesis defense.

INSERT INTO users VALUES (10000011, 'ringoADS', 'ringospassADS', 'student', 'Ringo', 'Starr', 'he/him', '1940-07-07', '310-859-9688', 'ringos@email.com', '500 E St.', 'New York', 'NY', 10001, null);
INSERT INTO students VALUES (10000011, 'PHD', null, null);
INSERT INTO enrolled_in VALUES (10000011, 0001, 'Fall', '2013', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0002,  'Fall', '2013', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0003,  'Fall', '2013', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0004,  'Fall', '2013', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0005,  'Fall', '2013', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0006,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0007,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0008,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0009,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0010,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0011,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (10000011, 0012,  'Spring', '2014', 'A');
--  completed CSCI 6221, 6212, 6461, 6232, 6233, 6241, 6242 and got B’s on these courses; and has completed CSCI 6283, 6284, 6286 and got A’s on these three courses. He graduated in 2014 with a MS degree.
INSERT INTO users VALUES (77777777, 'ericc', 'pass', 'alumni', 'Eric', 'Clapton', null, null, null, null, null, null, null, null, null);
INSERT INTO alumni VALUES (77777777, 'MS', '2014');
INSERT INTO enrolled_in VALUES (77777777, 0001, 'Fall', '2013', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0003,  'Fall', '2013', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0002,  'Fall', '2013', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0005,  'Fall', '2013', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0006,  'Fall', '2013', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0015,  'Spring', '2014', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0009,  'Spring', '2014', 'B');
INSERT INTO enrolled_in VALUES (77777777, 0013,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (77777777, 0014,  'Spring', '2014', 'A');
INSERT INTO enrolled_in VALUES (77777777, 0021,  'Spring', '2014', 'A');
-- Parmer is the advisor for Harrison and Ringo Starr
INSERT INTO users VALUES (17777777, 'gparmer', 'pass', 'fac_adv', 'Gabe', 'Parmer', null, null, null, null, null, null, null, null, null);
-- Narahari is advisor for McCartney
INSERT INTO users VALUES (27777777, 'adsnarahari', 'pass', 'fac_adv', 'Bhagi', 'Narahari', null, null, null, null, null, null, null, null, null);
INSERT INTO advises VALUES (66666666, 17777777);
INSERT INTO advises VALUES (10000011, 17777777);
INSERT INTO advises VALUES (55555555, 27777777);