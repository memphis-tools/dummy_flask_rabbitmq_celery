"""dummy example, we insert movies into a pdf"""

import os
from uuid import uuid4
import urllib.parse
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pymongo import MongoClient


load_dotenv("settings.py")

# We declare this variable as global in order to mock it during tests.
DUMMY_IMAGE_PATH = "dummy-ops.png"

# MongoDB encode username and password
ENCODED_USER = urllib.parse.quote_plus(os.getenv("MONGO_INITDB_ROOT_USERNAME"))
ENCODED_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_INITDB_ROOT_PASSWORD"))


def get_the_movies_list_from_mongodb() -> list:
    """Returns a list of movies as dictionnaries, from a mongodb database"""
    client = MongoClient(
        f'mongodb://{ENCODED_USER}:{ENCODED_PASSWORD}@{os.getenv("MONGO_SERVER")}:{os.getenv("MONGO_PORT")}/'
    )
    db = client[os.getenv("MONGO_DB_NAME")]
    collection = db[os.getenv("MONGO_COLLECTION_NAME")]
    documents = collection.find({}, {"_id": 0})
    movies_list = list(documents)
    return movies_list


def draw_multiline_text(c, text, x, y, max_width):
    """A function to format the movie description"""
    lines = []
    current_line = ""
    for word in text.split():
        if c.stringWidth(current_line + " " + word, "Helvetica", 12) < max_width:
            current_line += " " + word
        else:
            lines.append(current_line.strip())
            current_line = word
    lines.append(current_line.strip())

    for line in lines:
        c.drawString(x, y, line)
        y -= 14


def generate_a_pdf_to_consume() -> str:
    """A pdf generator function"""
    movies_list = get_the_movies_list_from_mongodb()
    items_per_page = 6
    total_pages = (len(movies_list) + items_per_page - 1) // items_per_page
    margin = 50
    image_size = 100
    pdf_folder_path = os.getenv("PDF_FOLDER_PATH")
    pdf_file_name = os.getenv("PDF_FILE_NAME")
    pdf_file_path = f"{pdf_folder_path}/{pdf_file_name}-{uuid4()}.pdf"

    # Create a pdf document
    c = canvas.Canvas(pdf_file_path, pagesize=A4)
    width, height = A4

    for page_num in range(total_pages):
        # Add image at the top with margin
        c.drawImage(
            DUMMY_IMAGE_PATH,
            width / 2 - image_size / 2,
            height - margin - image_size,
            width=image_size,
            height=image_size,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(
            width / 2, height - margin - image_size - 10, "Dummy Movies"
        )

        # Movie details
        c.setFont("Helvetica", 12)
        y_position = height - margin - image_size - 70
        start_index = page_num * items_per_page
        end_index = min(start_index + items_per_page, len(movies_list))

        for movie in movies_list[start_index:end_index]:
            if y_position - 60 < margin + 40:
                break  # Ensure there's space for the bottom image and pagination
            c.drawString(50, y_position, f"TITLE: {movie['title']}")
            y_position -= 20
            c.drawString(50, y_position, f"GENRE: {movie['genre']}")
            y_position -= 20
            c.drawString(50, y_position, f"YEAR: {movie['year']}")
            y_position -= 20
            c.drawString(50, y_position, f"RATING: {movie['rating']}")
            y_position -= 20
            description_text = f"DESCRIPTION: {movie['description']}"
            draw_multiline_text(c, description_text, 50, y_position, width - 100)
            y_position -= 50  # Space between movies

        # Adjust y_position for the bottom image and pagination
        y_position = margin + 40 if end_index == len(movies_list) else y_position

        # Pagination
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 40, 30, f"{page_num +1}/{total_pages}")

        # Add miniature image at the bottom center
        y_position = 60 if end_index == len(movies_list) else y_position
        c.drawImage(
            DUMMY_IMAGE_PATH,
            width / 2 - 15,
            margin,
            width=30,
            height=30,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Finish the page (used to finalize the current page and prepare for the next one)
        c.showPage()

    # Save the PDF
    c.save()
    return pdf_file_path
