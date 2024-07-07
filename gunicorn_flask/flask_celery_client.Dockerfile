FROM python:3.12.3-slim-bookworm

RUN apt-get update && apt-get install -y netcat-openbsd inetutils-ping

# create directory for the dummy-operator user
RUN mkdir -p /home/dummy-operator

# create the dummy-operator user
RUN addgroup --system dummy-operator && adduser --system --group dummy-operator

# create the appropriate directories
ENV HOME=/code/
ENV APP_HOME=/code/
RUN mkdir $APP_HOME;
RUN mkdir -p $APP_HOME/static_files/css;
RUN mkdir $APP_HOME/static_files/img;
RUN mkdir $APP_HOME/static_files/js;
RUN mkdir $APP_HOME/static_files/pdf;

WORKDIR $APP_HOME

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY ./gunicorn_flask/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy project
COPY ./celery_client_and_worker/app/ $APP_HOME/
COPY ./celery_client_and_worker/app/static/css/* $APP_HOME/static_files/css
COPY ./celery_client_and_worker/app/static/js/* $APP_HOME/static_files/js
COPY ./celery_client_and_worker/app/static/favicon.ico $APP_HOME/static_files/

EXPOSE 5000

# chown all the app files to the dummy-operator user
RUN chown -R dummy-operator:dummy-operator $APP_HOME
RUN chown -R dummy-operator:dummy-operator /code/static_files

USER dummy-operator
