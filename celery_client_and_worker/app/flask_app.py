"""The Flask app definition"""

import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from routes import routes_blueprint


app = Flask(__name__, static_folder="static_files", template_folder="templates")
app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL")
app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND")
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")
app.config["MAIL_USE_SSL"] = False

app.register_blueprint(routes_blueprint)
mail = Mail(app)
bootstrap = Bootstrap(app)
