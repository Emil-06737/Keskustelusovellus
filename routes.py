from app import app
from flask import render_template
import discussion_areas

@app.route("/")
def index():
    return render_template("index.html")