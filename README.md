The Midnight Times - News Search Application
This is a web application built with Django that allows users to search for news articles from around the world and view their search history.

Project Setup and Running Instructions
Follow these steps to get the project up and running on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

1. Clone the Repository (or setup the project)
   First, get the project code onto your machine. If it's in a git repository, clone it.

git clone https://github.com/vijay2909/News-Search.git
cd <project-directory>

2. Create and Activate a Virtual Environment
   It is highly recommended to use a virtual environment to manage project dependencies.

On macOS/Linux:

python3 -m venv venv
source venv/bin/activate

On Windows:

python -m venv venv
.\venv\Scripts\activate

3. Install Dependencies
   Install all the required packages using the requirements.txt file.

`pip install -r requirements.txt`

4. Apply Database Migrations
   This command will create the necessary database tables for the application, including the tables for users and profiles.

`python manage.py migrate`

5. Create a Superuser
   To access the Django admin panel, you need to create a superuser account.

`python manage.py createsuperuser`

You will be prompted to enter a username, email, and password.

6. Run the Development Server
   Now you can start the Django development server.

`python manage.py runserver`

7. Access the Application
   The application will be running at http://127.0.0.1:8000/.

Registration Page: http://127.0.0.1:8000/register/

Login Page: http://127.0.0.1:8000/login/

Admin Panel: http://127.0.0.1:8000/admin/ (Log in with your superuser credentials)

# To automatically refresh search results at a given interval.
`python manage.py setup_background_task`

Run the worker process in a separate terminal

`python manage.py process_tasks`

**Total time taken:** 6-7 Hours

# Development Experience

Working on this project over the course of 4 days, dedicating 1-2 hours each evening after office hours,
was both challenging and exciting. The assignment pushed me to deepen my understanding of Django’s core features,
including models, views, forms, and the admin interface. I enjoyed organizing the codebase into modular apps and 
implementing user authentication, custom forms, and background tasks.

Balancing this project with my regular work schedule required effective time management and focus. 
Each session brought new learning opportunities, from handling database migrations to automating periodic jobs with 
management commands. Overall, this experience significantly enhanced my skills in building scalable and maintainable 
Django applications, and increased my confidence in full-stack web development workflows.
