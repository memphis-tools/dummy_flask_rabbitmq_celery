import os
import json
import unittest
from dotenv import load_dotenv
from unittest.mock import patch, Mock
from celery_client_and_worker.app.flask_app import app
from celery_client_and_worker.app.celery_app import celery_app
from celery_client_and_worker.app.tasks import generate_pdf_and_send_email_task, send_email
from celery_client_and_worker.app.movies_into_pdf import generate_a_pdf_to_consume

load_dotenv("settings.py")

class TestCeleryTasks(unittest.TestCase):

    @patch('celery_client_and_worker.app.tasks.generate_a_pdf_to_consume')
    @patch('celery_client_and_worker.app.movies_into_pdf.DUMMY_IMAGE_PATH', 'celery_client_and_worker/app/dummy-ops.png')
    def test_generate_pdf_and_send_email_task_with_missing_movies_file(self, mock_generate_pdf):
        # Arrange
        mock_generate_pdf.return_value = '/mock/pdf/file.pdf'
        os.environ["MAIL_USERNAME"] = ""

        # Act
        result = generate_pdf_and_send_email_task()

        # Assert
        self.assertEqual(result['status'], 'failure')
        self.assertIn('Movies file not found', result['message'])


    @patch('celery_client_and_worker.app.movies_into_pdf.DUMMY_IMAGE_PATH', 'celery_client_and_worker/app/dummy-ops.png')
    def test_send_email(self):
        os.environ['PDF_FOLDER_PATH'] = "/tmp/"
        os.environ['PDF_FILE_NAME'] = "dummy_movies"

        # Arrange
        pdf_file_path = generate_a_pdf_to_consume()
        recipient = 'daisy@localhost'
        os.environ['MAIL_SENDER'] = 'test_sender'

        # Act
        with app.app_context():
            send_email(recipient, pdf_file_path)

        # Assert
        self.assertTrue(os.path.exists(pdf_file_path))
        os.remove(pdf_file_path)

if __name__ == '__main__':
    unittest.main()
