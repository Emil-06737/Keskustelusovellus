from sqlalchemy.sql import text
from db import db
from messages import create_message
from users import has_access_to_chain

def create_chain(header, area, creator, message):
    sql = """INSERT INTO discussion_chains (header, discussion_area_id, creator_id)
             VALUES (:header, :area, :creator) RETURNING id"""
    result = db.session.execute(text(sql), {"header":header, "area":area, "creator":creator})
    chain_id = result.fetchone().id
    create_message(message, chain_id, creator)

def get_stats(chain):
    sql = "SELECT header, discussion_area_id, creator_id FROM discussion_chains WHERE id=:chain"
    return db.session.execute(text(sql), {"chain":chain}).fetchone()

def get_accessed_chains():
    sql = "SELECT id FROM discussion_chains"
    chains = db.session.execute(text(sql)).fetchall()
    return [chain.id for chain in chains if has_access_to_chain(chain.id)]

def get_messages(chain):
    sql = """SELECT M.id, M.content, M.creator_id, M.sent_at, U.name FROM messages M, users U
             WHERE M.discussion_chain_id=:chain and U.id = M.creator_id ORDER BY M.id"""
    return db.session.execute(text(sql), {"chain":chain}).fetchall()

def modify_header(id1, header):
    sql = "UPDATE discussion_chains SET header=:header WHERE id=:id"
    db.session.execute(text(sql), {"header":header, "id":id1})
    db.session.commit()

def check_length(header):
    min1 = 3
    max1 = 50
    if len(header) < min1 or len(header) > max1:
        return (min1, max1)
    return None

def remove(chain):
    sql = "DELETE FROM discussion_chains WHERE id=:id"
    db.session.execute(text(sql), {"id":chain})
    db.session.commit()
