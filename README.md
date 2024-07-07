![Screenshot](https://img.shields.io/badge/python-v3.11-blue?logo=python&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/rabbitmq-v3.13.3-blue?logo=rabbitmq&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/redis-v5.0.6-blue?logo=redis&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/celery-v5.4.0-blue?logo=celery&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/nginx-v1.27.0-blue?logo=nginx&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/gunicorn-v22.0.0-blue?logo=gunicorn&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/flask-v3.0.3-blue?logo=flask&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/mongodb-v7.0.12-blue?logo=mongodb&logoColor=yellow)
![pylint and flake](https://github.com/memphis-tools/dummy_flask_rabbitmq_celery/actions/workflows/lint-flake.yml/badge.svg)
![pylint](https://img.shields.io/badge/PyLint-10.00-brightgreen?logo=python&logoColor=white)
![unittest](https://github.com/memphis-tools/dummy_flask_rabbitmq_celery/actions/workflows/run_tests.yml/badge.svg)


# DUMMY FLASK CELERY RABBITMQ REDIS APPLICATION

## Prerequisites

All services of this dummy illustration micro application are served through **Docker swarm**.

Set up and coding on a RedHat Linux OS based system. The following RPM should be used:

    python3-docker-pycreds >= 0.4.0-15
    python3-dockerpty >= 0.4.1-27
    python3-docker >= 5.0.3-3
    python3-docker+ssh >= 5.0.3-3
    docker-compose => 1.29.2-7
    docker-compose-plugin => 2.27.1-1
    docker-buildx-plugin => 0.14.1-1
    docker-ce-cli => 26.1.4-1
    docker-ce-rootless-extras => 26.1.4-1
    docker-ce >= 26.1.4-1

A running SMTP server at port 25 is required in order to have unittest tests succeeded (here postfix has been used), for a "tests" context.

To set a basic configuration for this service, you will use files to load environment vars: '.env.rc', '.env.rc.tests'

For the simulated "prod" context, suggestion is to use, for example, <a href="https://mailtrap.io/">MAILTRAP</a>.

## What is it ?

A dummy application for learning purposes deployed as a stack on docker swarm.

Aim is to execute asynchronous process, triggered by **Flask**, executed by a **Celery worker**.

**Flask** is the celery client. **Nginx** the reverse proxy to serve **Flask through Gunicorn**.

Task consist to send an email with a PDF file attached.

The PDF file content is a list of dummy movies pre-inserted in a MongoDB database.

For the POC we use mailtrap to simulate email reception.

A dummy Docker swarm.

<img src="illustrations/swarm.png" width="100%%" height="auto">

Some dummy Flask routes.

<img src="illustrations/flask.png" width="100%%" height="auto">

A dummy mailtrap account.

<img src="illustrations/mailtrap.png" width="100%%" height="auto">


## How it works ?

**Celery** workers use a default configuration.

**Rabbitmq** is setup with this default configuration (we just set a specific user, password and vhost).

We have a celery worker's cluster.

Celery uses 2 types of exchanges: fanout and direct.

The first one is a broadcast, which spread a task execution order, only 1 worker will execute the task.

The second one is for the celery worker to return message result to the rabbitmq queue.

    rabbitmqctl list_queues -p donald_vhost name messages

    rabbitmqctl list_bindings -p donald_vhost

<img src="illustrations/rabbitmq.png" width="100%%" height="auto">

The **Redis** database has a persistent volume. We can find all the transactions relative to the tasks execution from the celery workers.

<img src="illustrations/redis.png" width="100%%" height="auto">

The **MongoDB** will have a default dummy database created: "dummy_movies". And a dummy collection "movies", with 274 documents.

Once you entered the MongoDB container (replace username and password according to the ones defined in the compose file):

    mongosh --username [username] --password [passord] --authenticationDatabase admin

<img src="illustrations/mongodb.png" width="100%%" height="auto">

The swarm services need several timeouts. There is a simple usage of the 'sleep' UNIX command.

## How use it ?

For convenience, 2 dummy bash scripts are set. First you source either .env.rc or .env.rc.tests.

Example content of a **.env.rc** file:

    export SWARM_IP="0.0.0.0"
    export MONGO_INITDB_ROOT_USERNAME=admin
    export MONGO_INITDB_ROOT_PASSWORD=SuperPassword
    export MONGO_SERVER=localhost
    export MONGO_PORT=27017
    export MONGO_COLLECTION_NAME=movies
    export MONGO_DB_NAME=dummy_movies

    export RABBITMQ_DEFAULT_USER=donald
    export RABBITMQ_DEFAULT_PASS=SuperPassword
    export RABBITMQ_DEFAULT_VHOST=donald_vhost

    export CELERY_BROKER_URL='pyamqp://donald:SuperPassword@rabbitmq:5672/donald_vhost'
    export CELERY_RESULT_BACKEND='redis://redis:6379/0'
    export TIMEZONE='Europe/Paris'

    export MAIL_SERVER="sandbox.smtp.mailtrap.io"
    export MAIL_PORT="2525"
    export MAIL_USE_TLS=True
    export MAIL_USERNAME=yourMailTrapUserId
    export MAIL_PASSWORD=yourMailTrapUserPassword
    export MAIL_SENDER="flask@dummy-ops.localhost"

Example content of a **.env.rc.tests** file, will just be sligthly different from the previous one, just adapt these definitions:

    export MAIL_SERVER=localhost
    export MAIL_PORT=25
    export MAIL_USE_TLS=False
    export MAIL_USERNAME=""
    export MAIL_PASSWORD=""

As long as we start application in a "test" context, we run unittest.

In a production context, we do not need to source the venv and set the PYTHONPATH.

    source .env.rc
    ./start_application.sh

    source venv/bin/activate
    export PYTHONPATH=./celery_client_and_worker/app
    source .env.rc.tests
    ./start_application.sh -c test
    coverage run -m unittest -v

If you want to ask for one or more docker image to be rebuild:

    source .env.rc
    ./start_application.sh -r flask
    ./start_application.sh -r flask mongo redis

    source venv/bin/activate
    export PYTHONPATH=./celery_client_and_worker/app
    source .env.rc.tests
    ./start_application.sh -c test -r flask
    ./start_application.sh -c test -r flask mongo redis
    coverage run -m unittest -v

Notice: as celery worker tasks test involved to send a mail, you need a MTA service running at port 25 (postfix for example).

To stop the application only run:

    ./stop_application.sh

## How lint it ?

  pylint celery_client_and_worker/ mongodb/

  flake8 celery_client_and_worker/ mongodb/ --max-line-length=127 --count --statistics

## Usefull links

Learn rabbitmq: https://www.rabbitmq.com/tutorials

For the PDF creation: https://docs.reportlab.com/
