from os import getenv
from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

from users import create_admin
with app.app_context():
    create_admin(getenv("ADMIN_PASSWORD"))