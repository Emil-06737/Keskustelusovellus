import os
from app import app
from db import db
from flask import abort, request, session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
import discussion_areas

def login(name, password):
    sql = "SELECT id, name, password, admin FROM users WHERE name=:name"
    user = db.session.execute(text(sql), {"name":name}).fetchone()
    if not user:
        return False
    if not check_password_hash(user.password, password):
        return False
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_admin"] = user.admin
    session["csrf_token"] = os.urandom(16).hex()
    return True

def logout():
    del session["user_id"]
    del session["user_name"]
    del session["user_admin"]

def register(name, password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (name, password, admin) VALUES (:name, :password, :admin)"
        db.session.execute(text(sql), {"name":name, "password":hash_value, "admin":False})
        db.session.commit()
    except:
        return False
    return login(name, password)

def create_admin(password):
    with app.app_context():
        if not db.session.execute(text("SELECT 1 FROM users WHERE name = 'admin'")).fetchone():
            sql = "INSERT INTO users (name, password, admin) VALUES ('admin', :password, true)"
            db.session.execute(text(sql), {"password":password})
            db.session.commit()
        else:
            sql = "UPDATE users SET password = :password WHERE name = 'admin'"
            db.session.execute(text(sql), {"password":password})
            db.session.commit()

def require_admin():
    if not session["user_admin"]:
        abort(403)

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

def has_access_to_area(id):
    if discussion_areas.is_confidential(id):
        if not session.get("user_admin", False):
            users = discussion_areas.get_users_of_confidential_area(id)
            if session.get("user_id", 0) not in users:
                return False
    return True

def has_access_to_chain(chain):
    sql = "SELECT discussion_area_id FROM discussion_chains WHERE id=:chain"
    area = db.session.execute(text(sql), {"chain":chain}).fetchone()[0]
    return has_access_to_area(area)

def get_normal_users():
    sql = "SELECT id, name FROM users WHERE admin = False ORDER BY name"
    return db.session.execute(text(sql)).fetchall()