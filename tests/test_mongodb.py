import os
import unittest
import urllib.parse
from mongodb.init_mongo import get_the_movies_list, db, client, collection, ENCODED_USER, ENCODED_PASSWORD

class TestMoviesList(unittest.TestCase):
    def test_get_movies_list(self):
        """Test the get_the_movies_list function"""
        movies = get_the_movies_list()
        self.assertIsInstance(movies, list)
        self.assertGreater(len(movies), 0)
        self.assertIsInstance(movies[0], dict)
        self.assertIn("title", movies[0])
        self.assertIn("genre", movies[0])
        self.assertIn("year", movies[0])
        self.assertIn("rating", movies[0])
        self.assertIn("description", movies[0])

    def test_mongodb_connection(self):
        """Test the MongoDB client setup and database creation"""
        self.assertIsNotNone(client)
        self.assertIsNotNone(db)
        self.assertIn(os.getenv("MONGO_DB_NAME"), client.list_database_names())

    def test_insert_movies(self):
        """Test the insertion of movies into the MongoDB collection"""
        collection.delete_many({})
        movies = get_the_movies_list()
        collection.insert_many(movies)
        self.assertEqual(collection.count_documents({}), len(movies))

    def test_if_env_variables_set(self):
        """Test if required variables set"""
        self.assertIsNotNone(os.getenv("MONGO_INITDB_ROOT_USERNAME"))
        self.assertIsNotNone(os.getenv("MONGO_INITDB_ROOT_PASSWORD"))
        self.assertIsNotNone(os.getenv("MONGO_SERVER"))
        self.assertIsNotNone(os.getenv("MONGO_PORT"))
        self.assertIsNotNone(os.getenv("MONGO_DB_NAME"))
        self.assertIsNotNone(os.getenv("MONGO_COLLECTION_NAME"))


class TestMongoDBEncoding(unittest.TestCase):
    """Test the encoding of MongoDB username and password"""
    def test_mongodb_encoding(self):
        self.assertEqual(ENCODED_USER, urllib.parse.quote_plus(os.getenv("MONGO_INITDB_ROOT_USERNAME")))
        self.assertEqual(ENCODED_PASSWORD, urllib.parse.quote_plus(os.getenv("MONGO_INITDB_ROOT_PASSWORD")))


if __name__ == "__main__":
    unittest.main()
