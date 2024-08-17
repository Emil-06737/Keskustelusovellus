from db import db
from sqlalchemy.sql import text
from messages import create_message

def create_chain(header, area, creator, message):
    sql = """INSERT INTO discussion_chains (header, discussion_area_id, creator_id)
          VALUES (:header, :area, :creator) RETURNING id"""
    chain_id = db.session.execute(text(sql), {"header":header, "area":area, "creator":creator}).fetchone().id
    create_message(message, chain_id, creator)