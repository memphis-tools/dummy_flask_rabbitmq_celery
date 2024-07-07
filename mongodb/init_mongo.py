"""The Mongodb engine"""

import os
import json
import time
import urllib.parse
from pymongo import MongoClient

# Wait for MongoDB to start
time.sleep(3)

# MongoDB encode username and password
ENCODED_USER = urllib.parse.quote_plus(os.getenv("MONGO_INITDB_ROOT_USERNAME"))
ENCODED_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_INITDB_ROOT_PASSWORD"))


def get_the_movies_list() -> list:
    """A function to retrieve a movies list"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "movies.json")
    with open(json_file_path, "r", encoding="utf-8") as fd:
        movies_list = json.load(fd)
    return movies_list


# MongoDB client setup
client = MongoClient(
    f'mongodb://{ENCODED_USER}:{ENCODED_PASSWORD}@{os.getenv("MONGO_SERVER")}:{os.getenv("MONGO_PORT")}/'
)
db = client[os.getenv("MONGO_DB_NAME")]

if os.getenv("MONGO_DB_NAME") in client.list_database_names():
    client.drop_database(os.getenv("MONGO_DB_NAME"))

collection = db[os.getenv("MONGO_COLLECTION_NAME")]
collection.insert_many(get_the_movies_list())
