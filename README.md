# oauthsample

## Getting started

This is a basic django project with django-rest-framework.
To run the project, you can run the following commands:

- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py runserver`

## Authorization
This project uses the Oauth2 implementation for authentication/authorization.
Register an OAuth application with this:
- `http://localhost:8000/o/applications/`
Click on the link to create a new application and fill the form with the following data:

- Name: `settings.APPLICATION_NAME` value
- Client Type: confidential
- Authorization Grant Type: Resource owner password-based
- Save your app!

In case you face any issue with accessing the link, set a `LOGIN_URL` in your
settings file
`LOGIN_URL='/admin/login/'`

## Background Tasks
Background tasks are handled by Celery, with RabbitMQ as the broker.
RabbitMQ must be setup to successfully run the celery tasks.
