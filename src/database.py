"""
Darleine Abellard
Craft Watermark

Database logic for mapping watermark ids to their creators
"""

import sqlite3
from datetime import datetime, timezone

DB_PATH = "watermark.db"

def open_DB():
    """Opens (or creates) the SQLite database file

    Returns:
        sqlite3.Connection: an open database connection
    """
    connection = sqlite3.connect(DB_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS creators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_info TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS watermarked_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            image_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (creator_id) REFERENCES creators(id)
        )
    """)

    return connection

def register_creator(name, contact_info=None):
    """Creates a new creator record
    The returned id is the embedded watermark id in creator's images
    
    Args:
        name (str): the creator's display name
        contact_info (str, optional): private contact info (e.g. email)
        internal reference only

    Returns:
        int: the newly created creator's id
    """
    connection = open_DB()
    cursor = connection.execute(
        "INSERT INTO creators (name, contact_info) VALUES (?, ?)",
        (name, contact_info),
    )
    connection.commit()
    new_creator_id = cursor.lastrowid
    connection.close()
    return new_creator_id

def record_watermarked_image(creator_id, image_hash):
    """Records an image watermarked with creator_id 

    Args:
        creator_id (int): the id of the creator this image belongs to
        image_hash (str): the SHA256 hash (hex string) 
            of the watermarked img file contents

    Raises:
        sqlite3.IntegrityError: if creator_id doesn't correspond to a real creator
    """
    connection = open_DB()
    connection.execute(
        "INSERT INTO watermarked_images (creator_id, image_hash, created_at) VALUES (?, ?, ?)",
        (creator_id, image_hash, datetime.now(timezone.utc).isoformat())
    )
    connection.commit()
    connection.close()

def get_creator_by_id(creator_id):
    """Looks up a creator's info by their id

    Args:
        creator_id (int): the id to look up

    Returns:
        dict | None: the creator's info {"id", "name", "contact_info"},
            or None if no creator exists with that id
    """
    connection = open_DB()
    connection.row_factory = sqlite3.Row

    row = connection.execute(
        "SELECT id, name, contact_info FROM creators WHERE id = ?",
        (creator_id,),
    ).fetchone()
    connection.close()

    if row is None:
        return None
    return dict(row)