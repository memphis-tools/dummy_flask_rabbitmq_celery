FROM python:3.14.0rc2-slim-bookworm

RUN addgroup --system dummy-operator && adduser --system --group dummy-operator
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./celery_client_and_worker/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./celery_client_and_worker/app /code/
RUN chown -R dummy-operator:dummy-operator /code
EXPOSE 5555
USER dummy-operator
CMD ["celery", "-A", "celery_app", "worker", "-l", "INFO"]
