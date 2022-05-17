# University-System

This is flask powered application that interacts with an SQL database. 

This application provides a full univserity workflow. Name Hippo Campus, inspired by GWU, this is a graduate school. 

# Applying to the University
Prospective students are able to apply to the university if they submit a transcript and Hippo Campus recieves letters of recommendation for the prospective student. The system both supports MS and PhD students, decided upon in their application. Depending on what they would like to apply to the university for, it will change their requirements to be admitted and documentation required. This implentation was handled using JavaScript.

Faculty reviewers, faculy of HC, the review the student's application and report their decision. Based on their decisions, the application will move closer towards approval if a minimum of two reviewers approve. Here the graduate secretary must give a final decision for the student. If they are admitted, they become a student, otherwise they are removed from the system. 

# Students in the University
 
 Students now can view the course catalog and register for courses. The registration system prevents users from registering for conflicting times, courses that require prerequistes not met, and other errors. After a course is registered for, it will show in their current enrollment and display on their transcript as in progress. When a course is graded, their grade will display and their transcript will be recalculated. 

In order to graduate MS and PhD students must submit a Form 1. This is similar to a plan of study, this will check a student is taking the proper requirements to gradute and will alert a student if they are not. This plan of study checks items like credit hours and course requirements. A student has to then apply to graduate where the system will automatically audit their grades, course history, gpa, and more. If they are a PhD student, they must also have an approved final thesis from their faculty advisor. 


# Faculty Roles
  - Instructor : This user can assign grades and view their current students/classes.
  - Faculty Reviewer: This user reviews applications to HC and provides a decision on them. 
  - Faculty Advisor: This user can view its advisees transcripts, Form 1 (plan of study), and approves their PhD student's thesis. 
 
 # Admin Roles
  - Graduate Secretary : This user can view all applicants and their statuses. They can approve and deny applicants to HC. They also review applications to graduate, which they alone approve or deny. 
  - System Administrator : This user is a 'super' user. They can create any other kind of user and also delete any other user. They can also view all data and information on any of the users in the system and edit it. 

