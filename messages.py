from db import db
from sqlalchemy.sql import text
from users import has_access_to_chain

def create_message(message, chain, creator):
    sql = """INSERT INTO messages (content, discussion_chain_id, creator_id, sent_at)
             VALUES (:message, :chain, :creator, NOW())"""
    db.session.execute(text(sql), {"message":message, "chain":chain, "creator":creator})
    db.session.commit()

def get_information(id):
    sql = "SELECT content, discussion_chain_id, creator_id, sent_at FROM messages where id=:id"
    return db.session.execute(text(sql), {"id":id}).fetchone()

def modify_content(id, message):
    sql = "UPDATE messages SET content = :content WHERE id = :id"
    db.session.execute(text(sql), {"content":message, "id":id})
    db.session.commit()

def remove_message(id):
    sql = "DELETE FROM messages WHERE id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()

def check_length(message):
    min = 1
    max = 5000
    if len(message) < min or len(message) > max:
        return (min, max)
    else:
        return None

def search(query):
    sql = """SELECT m.content, m.discussion_chain_id, m.sent_at, u.name
             FROM messages m, users u WHERE m.creator_id = u.id AND content LIKE :query
             ORDER BY m.id DESC"""
    messages = db.session.execute(text(sql), {"query":"%"+query+"%"}).fetchall()
    accessed_messages = [message for message in messages if has_access_to_chain(message[1])]
    return accessed_messages
