def create_tables(db):
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT,
        color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    db.commit()