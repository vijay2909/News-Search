The Midnight Times - News Search Application
This is a web application built with Django that allows users to search for news articles from around the world and view their search history.

Project Setup and Running Instructions
Follow these steps to get the project up and running on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

1. Clone the Repository (or setup the project)
   First, get the project code onto your machine. If it's in a git repository, clone it.

git clone <your-repository-url>
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

pip install -r requirements.txt

4. Apply Database Migrations
   This command will create the necessary database tables for the application, including the tables for users and profiles.

python manage.py migrate

5. Create a Superuser
   To access the Django admin panel, you need to create a superuser account.

python manage.py createsuperuser

You will be prompted to enter a username, email, and password.

6. Run the Development Server
   Now you can start the Django development server.

python manage.py runserver

7. Access the Application
   The application will be running at http://127.0.0.1:8000/.

Registration Page: http://127.0.0.1:8000/register/

Login Page: http://127.0.0.1:8000/login/

Admin Panel: http://127.0.0.1:8000/admin/ (Log in with your superuser credentials)

# To automatically refresh search results at a given interval.
`python manage.py setup_background_task`

Run the worker process in a separate terminal

`python manage.py process_tasks`

Time Tracking
(Please fill this in)

Total time taken: [Your time here]

Development Experience
(Please fill this in)

[Share your overall experience working on this project here.]
