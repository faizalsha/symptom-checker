# Symptom Checker

## About:-

Symptom Checker is a platform which lets user to evaluate their health statuses and risk of having symptoms of some health issues, like Corona, Mental health issues etc.

Symptom checker allows Companies to become part of this platform and let them evaluate the health status of their employees. They can select the questionnaires which are available on the platform to be used in their companies.

## Technologies Used.

Symptom Checker is formed on Django Python Framework. We used Celery with Redis for handling Async Tasks.

## Setup

Follow the following steps to set this up locally.

1. Clone this repository with command:-\
   $git clone https://code.jtg.tools/inductions/induction-2021/induction-jan-2021/symptom-checker.git

2. Create virtual environment for the project:\
   $python3 -m venv env

3. Install project dependencies from requirement.txt by following command.\
   $pip install -r requirement.txt

4. Move to the directory Backend:\
   $cd symptom-checker/backend

5. Go to settings folder and make a file local.py by lines of code from local.template file.\
   (We have used Postgres for database, in case you want to use someother database refer docs -> https://docs.djangoproject.com/en/2.2/ref/databases/)

6. Create a '.env' file in settings folder with credentials:-\
   i. DB_NAME\
   ii. DB_USER\
   iii. DB_PASSWORD\
   iv. EMAIL_ID\
   v.EMAIL PASSWORD

7. Run migrations for the project:\
   $ python manage.py migrate

8. For Async Task Celery with Redis used, hence you need to install install redis from this link -> https://redis.io/download

9. Create Super user for accessing admin panel:-\
   $ python manage.py createsuperuser

10. Run the server by command:-\
    $ python manage.py runserver

11. For starting Celery Instance run following command in a new terminal:-\
    $ celery -A backend worker -l INFO

Your project setup will be completed after following these steps. Now you can see the avaliable API endpoints by going to http://127.0.0.1:8000/swagger/ . For accessing admin panel go to http://127.0.0.1:8000/admin/ .

For Running this project on Dev Or Prod Settings simply export DJANGO_SETTINGS_MODULE and DJANGO_CONFIGURATION as (settings.backend.dev, Dev) or (settings.backend.prod, Prod) respectively.
