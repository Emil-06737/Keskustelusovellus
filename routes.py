from app import app
from flask import render_template, request, redirect
import discussion_areas
import users

@app.route("/")
def index():
    return render_template("index.html", areas=discussion_areas.get_stats())

@app.route("/login", methods=["get", "post"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]

        if not users.login(name, password):
            return render_template("error.html", message="Väärä tunnus tai salasana.")
        return redirect("/")
    
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")