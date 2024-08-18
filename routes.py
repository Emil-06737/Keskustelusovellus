from app import app
from flask import render_template, request, redirect, session
import discussion_areas
import discussion_chains
import messages
import users

@app.route("/")
def index():
    return render_template("index.html", areas=discussion_areas.get_accessed_stats())

@app.route("/area/<int:area_id>")
def area(area_id):
    if not users.has_access_to_area(area_id):
        return render_template("error.html", message="Ei oikeutta nähdä sivua.")
    area_topic = discussion_areas.get_topic(area_id)
    area_chains = discussion_areas.get_chains(area_id)
    return render_template("area.html", id=area_id, topic=area_topic, chains=area_chains)

@app.route("/chain/<int:chain_id>")
def chain(chain_id):
    if not users.has_access_to_chain(chain_id):
        return render_template("error.html", message="Ei oikeutta nähdä sivua.")
    messages1 = discussion_chains.get_messages(chain_id)
    chain1 = discussion_chains.get_stats(chain_id)
    return render_template("chain.html", id=chain_id, chain=chain1, messages=messages1)


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
            return render_template("error.html", message="Tunnuksessa tulee olla 3-20 merkkiä.")
        
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat.")
        if password1 < 5 or password1 > 100:
            return render_template("error.html", message="Salasanan tulee olla 5-100 merkkiä.")
        
        if not users.register(username, password1):
            return render_template("error.html", message="Rekisteröinti ei onnistunut.")
        return redirect("/")
    
@app.route("/create-area", methods=["post"])
def create_area():
    users.check_csrf()
    users.require_admin()

    topic = request.form["topic"]
    if len(topic) < 3 or len(topic) > 50:
        return render_template("error.html", message="Aiheen tulee olla 3-50 merkkiä.")

    secret=request.form["secret"]

    if int(secret) not in [0, 1]:
        return render_template("error.html", message="Vääränlainen salaisuus.")
    
    if not discussion_areas.add_discussion_area(topic, secret):
        message1 = "Samanaiheinen keskustelualue on jo olemassa."
        return render_template("error.html", message=message1)
    
    return redirect("/")

@app.route("/create-chain", methods=["post"])
def create_chain():
    users.check_csrf()

    header = request.form["header"]
    if len(header) < 3 or len(header) > 50:
        return render_template("error.html", message="Otsikon tulee olla 3-50 merkkiä.")
    
    message = request.form["message"]
    minmax = messages.check_length(message)
    if minmax:
        message1 = f"Viestin tulee olla {minmax[0]}-{minmax[1]} merkkiä."
        return render_template("error.html", message=message1)
    
    area_id = int(request.form["area_id"])
    if area_id not in [area.id for area in discussion_areas.get_accessed_stats()]:
        return render_template("error.html", message="Väärä keskustelualue.")
    
    discussion_chains.create_chain(header, area_id, session["user_id"], message)

    return redirect(f"/area/{area_id}")

@app.route("/create-message", methods=["post"])
def create_message():
    users.check_csrf()

    message = request.form["message"]
    minmax = messages.check_length(message)
    if minmax:
        message1 = f"Viestin tulee olla {minmax[0]}-{minmax[1]} merkkiä."
        return render_template("error.html", message=message1)
    
    chain_id = int(request.form["chain_id"])
    if chain_id not in discussion_chains.get_accessed_chains():
        return render_template("error.html", message="Väärä keskusteluketju.")
    
    messages.create_message(message, chain_id, session["user_id"])

    return redirect(f"/chain/{chain_id}")