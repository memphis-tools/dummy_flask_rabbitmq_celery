"""The celery worker's tasks"""

import os
from dotenv import load_dotenv
from flask_mail import Message
from celery_app import celery_app
from flask_app import app, mail

from movies_into_pdf import generate_a_pdf_to_consume

load_dotenv("settings.py")


@celery_app.task(name="generate_pdf_and_send_email_task")
def generate_pdf_and_send_email_task():
    """The task ran by celery worker"""
    recipient = f'{os.getenv("MAIL_USERNAME")}@mailtrap.com'
    with app.app_context():
        try:
            pdf_file_path = generate_a_pdf_to_consume()
            send_email(recipient, pdf_file_path)
            os.remove(pdf_file_path)
            return {
                "status": "success",
                "message": f"Email sent successfully to {recipient}",
            }
        except FileNotFoundError:
            return {"status": "failure", "message": "Movies file not found"}


def send_email(recipient, pdf_file_path):
    """A send email function triggered by the celery worker's task"""
    with open(pdf_file_path, "rb") as fd:
        pdf_data = fd.read()
    sender = os.getenv("MAIL_SENDER")
    pdf_file_name = os.getenv("PDF_FILE_NAME")
    msg = Message(
        "Your dummy movies in a PDF File", sender=sender, recipients=[recipient]
    )
    msg.body = "Hello, thanks for using the service. Please find attached the document."
    msg.attach(pdf_file_name, "application/pdf", pdf_data)
    mail.send(msg)
