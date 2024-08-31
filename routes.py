from flask import render_template, request, redirect, session, abort
from app import app
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
        if len(password1) < 5 or len(password1) > 100:
            return render_template("error.html", message="Salasanan tulee olla 5-100 merkkiä.")

        if not users.register(username, password1):
            return render_template("error.html", message="Rekisteröinti ei onnistunut.")
        return redirect("/")

@app.route("/create-area", methods=["get", "post"])
def create_area():
    if request.method == "GET":
        users.require_admin()
        return render_template("create_area.html", users=users.get_normal_users())

    if request.method == "POST":
        users.check_csrf()
        users.require_admin()

        topic = request.form["topic"]
        if len(topic) < 3 or len(topic) > 50:
            return render_template("error.html", message="Aiheen tulee olla 3-50 merkkiä.")

        secret = request.form["secret"]

        if int(secret) not in [0, 1]:
            return render_template("error.html", message="Vääränlainen salaisuus.")

        secret_users = request.form.getlist("user")
        normal_users_ids = [user.id for user in users.get_normal_users()]
        for secret_user in secret_users:
            if int(secret_user) not in normal_users_ids:
                abort(403)

        if not discussion_areas.add_discussion_area(topic, secret, secret_users):
            message1 = "Samanaiheinen keskustelualue on jo olemassa."
            return render_template("error.html", message=message1)

        return redirect("/")

@app.route("/create-chain", methods=["post"])
def create_chain():
    users.check_csrf()

    header = request.form["header"]
    minmax = discussion_chains.check_length(header)
    if minmax:
        message2 = f"Otsikon tulee olla {minmax[0]}-{minmax[1]} merkkiä."
        return render_template("error.html", message=message2)

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

@app.route("/modify-chain-header", methods=["post"])
def modify_chain_header():
    users.check_csrf()
    id1 = request.form["id"]
    if discussion_chains.get_stats(int(id1))[2] != session["user_id"]:
        return render_template("error.html", message="Ei oikeutta muokata tätä otsikkoa.")
    header = request.form["header"]
    minmax = discussion_chains.check_length(header)
    if minmax:
        message1 = f"Otsikon tulee olla {minmax[0]}-{minmax[1]} merkkiä."
        return render_template("error.html", message=message1)
    discussion_chains.modify_header(id1, header)
    return redirect(f"/chain/{id1}")

@app.route("/remove-chain", methods=["post"])
def remove_chain():
    users.check_csrf()

    id1 = request.form["id"]
    chain_stats = discussion_chains.get_stats(id1)
    if not chain_stats:
        abort(403)
    if chain_stats[2] != session.get("user_id", 0):
        abort(403)

    discussion_chains.remove(id1)
    return redirect(f"/area/{chain_stats[1]}")

@app.route("/modify-message", methods=["post"])
def modify_message():
    users.check_csrf()
    id1 = request.form["id"]
    message = request.form["message"]
    message_information = messages.get_information(id1)
    if (session.get("user_id", 0) != message_information[2]) or messages.check_length(message):
        abort(403)

    messages.modify_content(id1, message)
    return redirect(f"/chain/{message_information[1]}")

@app.route("/remove-message", methods=["post"])
def remove_message():
    users.check_csrf()
    id1 = request.form["id"]
    message_information = messages.get_information(id1)
    if session.get("user_id", 0) != message_information[2]:
        abort(403)

    messages.remove_message(id1)
    return redirect(f"/chain/{message_information[1]}")

@app.route("/result")
def result():
    query = request.args["query"]
    return render_template("result.html", messages=messages.search(query), query=query)

@app.route("/remove-area", methods=["post"])
def remove_area():
    users.check_csrf()
    if not session.get("user_admin", False):
        abort(403)
    discussion_areas.remove_area(request.form["id"])
    return redirect("/")

@app.route("/choose-users", methods=["get", "post"])
def choose_users():
    users.require_admin()

    if request.method == "GET":
        id1 = request.args["id"]
        secret = discussion_areas.is_confidential(id1)
        n_users = users.get_normal_users()
        s_users = discussion_areas.get_users_of_confidential_area(id1)
        topic1 = discussion_areas.get_topic(id1)
        return render_template("choose_users.html", id=id1, confidentiality=secret,
                               normal_users=n_users, secret_users=s_users, topic=topic1)

    if request.method == "POST":
        users.check_csrf()
        id1 = request.form["id"]
        confidentiality = request.form["secret"]
        secret_users = request.form.getlist("user")
        if int(id1) not in [area[0] for area in discussion_areas.get_stats()]:
            abort(403)
        if int(confidentiality) not in [0, 1]:
            abort(403)
        normal_users_ids = [user.id for user in users.get_normal_users()]
        for secret_user in secret_users:
            if int(secret_user) not in normal_users_ids:
                abort(403)

        discussion_areas.update_users(id1, confidentiality, secret_users)
        return redirect(f"/area/{id1}")
