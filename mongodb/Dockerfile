FROM mongo:latest

RUN apt-get update && apt-get install -y python3 python3-pip python3.12-venv

COPY ./mongodb/entrypoint.sh /docker-entrypoint-initdb.d/entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/entrypoint.sh

COPY ./mongodb/init_mongo.py /docker-entrypoint-initdb.d/
COPY ./mongodb/movies.json /docker-entrypoint-initdb.d/
COPY ./mongodb/requirements.txt /requirements.txt
RUN python3.12 -m venv .venv
RUN . .venv/bin/activate
RUN .venv/bin/python3 -m pip install -r /requirements.txt

VOLUME /data/db

EXPOSE 27017

CMD ["mongod"]
