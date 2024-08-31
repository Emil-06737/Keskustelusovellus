from db import db
from sqlalchemy.sql import text
from users import has_access_to_area

def get_stats():
    sql = """SELECT da.id, da.topic, COUNT(DISTINCT dc.id), COUNT(m.id), MAX(m.sent_at)
             FROM discussion_areas da LEFT JOIN discussion_chains dc
             ON da.id = dc.discussion_area_id LEFT JOIN messages m ON dc.id = m.discussion_chain_id
             GROUP BY da.id ORDER BY da.id"""
    return db.session.execute(text(sql)).fetchall()

def get_accessed_stats():
    return [area for area in get_stats() if has_access_to_area(area.id)]

def add_discussion_area(topic, confidentiality, users=None):
    try:
        sql = """INSERT INTO discussion_areas (topic, confidential)
                 VALUES (:topic, :confidentiality) RETURNING id"""
        result = db.session.execute(text(sql), {"topic":topic, "confidentiality":confidentiality})
        id = result.fetchone().id
        if confidentiality and users:
            add_users_to_secret_area(id, users)
        db.session.commit()
        return True
    except:
        return False

def update_users(id, confidentiality, users=None):
    remove_users_of_secret_area(id)
    if users:
        add_users_to_secret_area(id, users)
    update_confidentiality(id, confidentiality)
    db.session.commit()

def remove_users_of_secret_area(area_id):
    sql = "DELETE FROM users_of_confidential_discussion_areas WHERE discussion_area_id = :area_id"
    db.session.execute(text(sql), {"area_id":area_id})

def update_confidentiality(area_id, confidentiality):
    sql = "UPDATE discussion_areas SET confidential = :confidentiality WHERE id = :area_id"
    db.session.execute(text(sql), {"area_id":area_id, "confidentiality":confidentiality})

def add_users_to_secret_area(id, users):
    for user in users:
        sql = """INSERT INTO users_of_confidential_discussion_areas (discussion_area_id, user_id)
                 VALUES (:id, :user)"""
        db.session.execute(text(sql), {"id":id, "user":user})

def is_confidential(id):
    sql = "SELECT confidential FROM discussion_areas WHERE id = :id"
    return db.session.execute(text(sql), {"id":id}).fetchone()[0]

def get_users_of_confidential_area(id):
    sql = """SELECT user_id FROM users_of_confidential_discussion_areas
             WHERE discussion_area_id = :id"""
    list = db.session.execute(text(sql), {"id":id}).fetchall()
    return [row[0] for row in list]

def get_chains(id):
    sql = "SELECT id, header FROM discussion_chains WHERE discussion_area_id = :id ORDER BY id"
    return db.session.execute(text(sql), {"id":id}).fetchall()

def get_topic(id):
    sql = "SELECT topic FROM discussion_areas WHERE id = :id"
    return db.session.execute(text(sql), {"id":id}).fetchone()[0]

def remove_area(id):
    sql = "DELETE FROM discussion_areas WHERE id = :id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()