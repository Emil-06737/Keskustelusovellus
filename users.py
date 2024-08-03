import os
from db import db
from flask import session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash

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