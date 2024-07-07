import unittest
from flask import url_for
from celery_client_and_worker.app.flask_app import app
from celery_client_and_worker.app.celery_app import celery_app
from unittest.mock import patch, Mock


class TestGetMovies(unittest.TestCase):
    """Test Flask routes"""

    def setUp(self):
        self.flask_client = app.test_client()

    def test_home_route(self):
        """Test the home route"""
        response = self.flask_client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the PDF download example", response.data)


    def test_books_route(self):
        """Test the books route"""
        with app.test_client() as client:
            response = client.get('/books')
            assert response.status_code == 200
            assert b"Here you should have some books illustrated sir" in response.data


    def test_movies_route(self):
        """Test the movies route"""
        response = self.flask_client.get('/movies')
        assert response.status_code == 200
        assert b"Here you should have some movies illustrated sir" in response.data


    @patch('celery_app.celery_app.send_task')
    def test_mail_movies_route_sends_task_with_retry(self, mock_send_task):
        response = self.flask_client.get("/mail_movies")
        # Assert that the task is sent
        mock_send_task.assert_called_once_with(
            "generate_pdf_and_send_email_task", args=(), retry=True
        )
        assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
