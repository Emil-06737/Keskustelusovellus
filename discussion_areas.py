from db import db
from sqlalchemy.sql import text

def get_stats():
    sql = """SELECT da.id, da.topic, COUNT(dc.id), COUNT(m.id), MAX(m.sent_at)
             FROM discussion_areas da LEFT JOIN discussion_chains dc
             ON da.id = dc.discussion_area_id LEFT JOIN messages m ON dc.id = m.discussion_chain_id
             GROUP BY da.id ORDER BY da.id"""
    return db.session.execute(text(sql)).fetchall()

def add_discussion_area(topic, confidentiality):
    try:
        sql = "INSERT INTO discussion_areas (topic, confidential) VALUES (:topic, :confidentiality)"
        db.session.execute(text(sql), {"topic":topic, "confidentiality":confidentiality})
        db.session.commit()
        return True
    except:
        return False