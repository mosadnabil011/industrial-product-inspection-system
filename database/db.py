import sqlite3

DB_NAME = "Production_DB.db"


def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    from database.models import create_tables
    db = get_db()
    create_tables(db)
    db.close()
    
