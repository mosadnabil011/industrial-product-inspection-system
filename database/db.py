import sqlite3
from database.models import create_tables
DB_NAME = "Production_DB.db"


def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    db = get_db()
    create_tables(db)
    db.close()

