"""The Flask routes"""

from celery_app import celery_app
from flask import Blueprint, render_template


routes_blueprint = Blueprint("routes", __name__)


@routes_blueprint.route("/")
@routes_blueprint.route("/home")
@routes_blueprint.route("/index")
def home():
    """a home Flask route"""
    return render_template("home.html")


@routes_blueprint.route("/books")
def books():
    """a books Flask route"""
    return render_template("books.html")


@routes_blueprint.route("/movies")
def movies():
    """a movies Flask route"""
    return render_template("movies.html")


@routes_blueprint.route("/mail_movies")
def mail_movies():
    """a mail_movies Flask route"""
    celery_app.send_task("generate_pdf_and_send_email_task", args=(), retry=True)
    return render_template("mail_movies.html")
