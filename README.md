# 0708784001
# Adaptive Learning Platform
#### Video Demo: https://youtu.be/96RNwYfO_Cc
#### Description:
    Overview
    The Adaptive Learning Platform is a full-stack web application built using Flask, SQLite, and Jinja2 templates. It is designed to offer a personalized educational experience for users, allowing them to sign up, log in securely, browse courses, enroll and track progress. The platform also displays upcoming educational events and aims to evolve into a fully adaptive system that adjusts to users' learning behaviors and needs.

    This project was inspired by the growing demand for digital learning environments that are user-centered, secure, and extensible. With a core focus on functionality, security and modular design, the platform serves as a strong foundation for more advanced learning management systems (LMS) in the future.


    Routes and Their Purpose
    The core application logic resides in `app.py`, the main Flask application file. Each route performs a specific function to ensure smooth user interaction and secure navigation:

    `/signup`
    The '/signup' functionality allows new users to register by submitting a username, password and confirming the password through a web form. The logic behind this route is designed to ensure both usability and security. First, the system validates user input to make sure that all required fields are filled out correctly and that the password and its confirmation match. It then checks whether the chosen username already exists in the database to prevent duplicates. If the username is unique, the password is securely hashed using `generate_password_hash` before being stored. Finally, the new user's credentials are added to the `users` table in the database, completing the registration process.

    `/signin`
    The `/signin` route handles user login by validating and authenticating user credentials. When a user submits their username and password, the system first checks that both fields are provided. It then queries the database to retrieve the stored password hash associated with the submitted username. To ensure security, the submitted password is compared against the stored hash using `check_password_hash`, which prevents direct exposure of the original password. If the credentials are valid, the application initializes a session by storing the user's ID, effectively logging them in and granting access to protected areas of the platform.

    `/logout`
    Clears the user session and redirects to the sign-in page with a confirmation flash message.

    `/forgot`
    Allows users to reset their password by verifying their username and updating the password hash. Ensures password confirmation matches before updating.

    `/` (Home)
    A protected route that renders the homepage after successful login. It acts as the user’s entry point to the application.

    `/dashboard`
    The `/dashboard` route serves as the most dynamic and user-centric page in the application, accessible exclusively to authenticated users. Upon accessing this route, the system first verifies that the user is logged in by checking session data. The dashboard then aggregates and displays personalized information, starting with a complete list of all available courses retrieved from the `courses` table. It also shows the specific courses in which the user is currently enrolled, along with their progress, by querying the `user_courses` table. Additionally, the dashboard features a section for upcoming events, such as webinars or deadlines, which are pulled from the `events` table and ordered by date. This combination of general and user-specific content makes the dashboard the central hub for a learner’s ongoing activity within the platform.


    Templates Overview
    The platform uses Jinja2 templates stored in the `templates/` folder. These HTML files form the frontend UI, dynamically populated with data passed from Flask routes:

    `layout.html`
    The `layout.html` file is the main template that all other HTML templates in the application extend from. It includes a Bootstrap-styled navigation bar for easy navigation, a section to display flash messages to users, and a `{% block content %}` placeholder where each page’s unique content is inserted. It also contains links to static resources like CSS or JavaScript files if needed. By using this base layout, the application ensures a consistent user interface across all pages and avoids repeating the same code, following the DRY (Don't Repeat Yourself) principle.

    `signin.html`
    The `signin.html` template is a login form where users can enter their credentials to access the platform. It includes input fields for the username and password, allowing users to submit their details. If there are any login errors, such as incorrect credentials, flash messages are displayed to inform the user. Additionally, the template provides navigation links to the registration page for new users and the password recovery page for users who have forgotten their login details.

    `signup.html`
    The `signup.html` template is a form for new user registration. It includes input fields for the username, password, and password confirmation, allowing users to create an account. The form validates that the password and its confirmation match, and checks that the chosen username is not already taken. If there are any issues, the user is notified with error messages. Once the registration is successful, users are redirected to the sign-in page to log in with their newly created account.

    `forgot.html`
    The `forgot.html` template is a password reset form that allows users to update their password. It includes input fields for the username, new password, and password confirmation. The form checks for valid input, ensuring that all fields are filled out correctly and that the new password matches the confirmation. It also verifies that the provided username exists in the database. To enhance security, the form prevents blank or mismatched password submissions, guiding users to submit valid and secure information.

    `dashboard.html`
    The `dashboard.html` template displays dynamic, user-specific content that is tailored to each logged-in user. It lists all available courses from the `courses` table, allowing users to browse through the full catalog. The page also shows the courses the user is currently enrolled in, along with their progress, pulled from the `user_courses` table. Additionally, it highlights upcoming events, such as webinars or deadlines, in chronological order by querying the `events` table. The layout is designed to be easily scalable, allowing for the future addition of features like learning analytics or personalized course recommendations.

    `home.html`
    Simple landing page shown post-signin. Acts as a welcome screen and placeholder for future user-specific announcements or activity highlights.

