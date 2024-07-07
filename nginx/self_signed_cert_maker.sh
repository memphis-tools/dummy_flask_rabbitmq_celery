#!/bin/bash

# self_signed_cert_maker
# generates dummy nginx certs either for a "test" context or any other
# if parameter $1 exists, it'll be the name of the NGINX certs folder

openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout ./$1/dummy_flask_rabbitmq_celery.key \
    -out ./$1/dummy_flask_rabbitmq_celery.crt \
    -days 3650 \
    -subj "/C=FR/ST=IDF/L=PARIS/O=DUMMY_OPS_TEAM/CN=dummy_flask_rabbitmq_celery.dev"
