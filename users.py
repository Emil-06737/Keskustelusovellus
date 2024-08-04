import os
from db import db
from flask import session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

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