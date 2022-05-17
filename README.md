# University-System

Created in collaboration with @ryah349 and @josielibbon.

This is flask powered application that interacts with an SQL database. 
This application provides a full univserity workflow. Name Hippo Campus, inspired by GWU, this is a graduate school. 

The application implements the use of connection to database, which at the time of its creation was powered on AWS. The website itself was also hosted on AWS. All users information for the site is stored in the database. The schema contains a central table of users for the system, and then relations to the users table for specific kinds of users. Additionally, it stores all of the data for the application, including courses, a student's history, applications, and much more. The database satifies 3NF. 

The application utilizes session variables to keep track of users. Security for the site is also dependent on session variables. For any given route a user accesses, it will check the session variable first to ensure that user has access. If they do not it will reroute them out of the system and clear all sessions. 

This project implements Bootstrap for uniform html styling across all pages. Javascript is implemented on pages requiring different support for different users. 


# Applying to the University
Prospective students are able to apply to the university if they submit a transcript and Hippo Campus recieves letters of recommendation for the prospective student. The system both supports MS and PhD students, decided upon in their application. Depending on what they would like to apply to the university for, it will change their requirements to be admitted and documentation required. This implentation was handled using JavaScript.

Faculty reviewers, faculy of HC, the review the student's application and report their decision. Based on their decisions, the application will move closer towards approval if a minimum of two reviewers approve. Here the graduate secretary must give a final decision for the student. If they are admitted, they become a student, otherwise they are removed from the system. 

# Students in the University
 
 Students now can view the course catalog and register for courses. The registration system prevents users from registering for conflicting times, courses that require prerequistes not met, and other errors. After a course is registered for, it will show in their current enrollment and display on their transcript as in progress. When a course is graded, their grade will display and their transcript will be recalculated. 

In order to graduate MS and PhD students must submit a Form 1. This is similar to a plan of study, this will check a student is taking the proper requirements to gradute and will alert a student if they are not. This plan of study checks items like credit hours and course requirements. A student has to then apply to graduate where the system will automatically audit their grades, course history, gpa, and more. If they are a PhD student, they must also have an approved final thesis from their faculty advisor. If they are approved, they become alumni of HC. 


# Faculty Roles
  - Instructor : This user can assign grades and view their current students/classes.
  - Faculty Reviewer: This user reviews applications to HC and provides a decision on them. 
  - Faculty Advisor: This user can view its advisees transcripts, Form 1 (plan of study), and approves their PhD student's thesis. 
 
 # Admin Roles
  - Graduate Secretary : This user can view all applicants and their statuses. They can approve and deny applicants to HC. They also review applications to graduate, which they alone approve or deny. 
  - System Administrator : This user is a 'super' user. They can create any other kind of user and also delete any other user. They can also view all data and information on any of the users in the system and edit it. 

# Example Views

<img width="748" alt="Screen Shot 2022-05-17 at 12 01 13 PM" src="https://user-images.githubusercontent.com/73393532/168861973-4eb54e06-b01c-4870-a95f-e6e36b24bcc3.png">

Transcript view for an Alumni.

<img width="713" alt="Screen Shot 2022-05-17 at 12 01 29 PM" src="https://user-images.githubusercontent.com/73393532/168862016-05d255c3-db8d-4523-baf2-069ec1280b71.png">

Faculty Advisor view for their Advisees.

<img width="714" alt="Screen Shot 2022-05-17 at 12 02 40 PM" src="https://user-images.githubusercontent.com/73393532/168862052-cbe86ac5-aa4d-4dd8-b9d2-d8c9bb0f2301.png">

Assigning an advisor with the Graduate Secretary View. 

<img width="710" alt="Screen Shot 2022-05-17 at 12 02 17 PM" src="https://user-images.githubusercontent.com/73393532/168862035-17e65a95-8684-421f-a195-7de3310e0a58.png">

Reviewing applications to graduate with the Graduate Secretary View. 

<img width="715" alt="Screen Shot 2022-05-17 at 12 25 26 PM" src="https://user-images.githubusercontent.com/73393532/168862080-2f60414e-2602-4613-98d6-9b401f40a561.png">

Security screen displayed when accessing an unauthorized route.




