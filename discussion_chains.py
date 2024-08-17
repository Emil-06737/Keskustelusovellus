from db import db
from sqlalchemy.sql import text
from messages import create_message
from users import has_access_to_chain

def create_chain(header, area, creator, message):
    sql = """INSERT INTO discussion_chains (header, discussion_area_id, creator_id)
          VALUES (:header, :area, :creator) RETURNING id"""
    chain_id = db.session.execute(text(sql), {"header":header, "area":area, "creator":creator}).fetchone().id
    create_message(message, chain_id, creator)

def get_stats(chain):
    sql = "SELECT header, discussion_area_id, creator_id FROM discussion_chains WHERE id=:chain"
    return db.session.execute(text(sql), {"chain":chain}).fetchone()

def get_accessed_chains():
    sql = "SELECT id FROM discussion_chains"
    chains = db.session.execute(text(sql)).fetchall()
    return [chain.id for chain in chains if has_access_to_chain(chain.id)]

def get_messages(chain):
    sql = "SELECT id, content, creator_id, sent_at FROM messages WHERE discussion_chain_id=:chain"
    return db.session.execute(text(sql), {"chain":chain}).fetchall()