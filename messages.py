from db import db
from sqlalchemy.sql import text

def create_message(message, chain, creator):
    sql = """INSERT INTO messages (content, discussion_chain_id, creator_id, sent_at)
             VALUES (:message, :chain, :creator, NOW())"""
    db.session.execute(text(sql), {"message":message, "chain":chain, "creator":creator})
    db.session.commit()

def check_length(message):
    min = 1
    max = 5000
    if len(message) < min or len(message) > max:
        return (min, max)
    else:
        return None