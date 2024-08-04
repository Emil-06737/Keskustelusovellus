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

@app.route("/register", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form["username"]
        if len(username) < 3 or len(username) > 20:
            return render_template("error.html", message="Tunnuksessa tulee olla 3-20 merrkiä.")
        
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat.")
        if password1 == "":
            return render_template("error.html", message="Salasana on tyhjä.")
        
        if not users.register(username, password1):
            return render_template("error.html", message="Rekisteröinti ei onnistunut.")
        return redirect("/")