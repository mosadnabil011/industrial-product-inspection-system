import sqlite3
from datetime import datetime
from random import choice

DB_NAME = "Production_DB.db"

db = sqlite3.connect(DB_NAME)
cursor = db.cursor()
statuses = ["OK", "NOT_OK"]  # بدل "ok", "not_ok"
colors = ["red", "green", "blue", "yellow", "orange"]

for _ in range(50):  # عدد الصفوف اللي تحب تضيفه
    status = choice(statuses)
    color = choice(colors)
    cursor.execute(
        "INSERT INTO products (status, color, created_at) VALUES (?, ?, ?)",
        (status, color, datetime.now())
    )

db.commit()
db.close()
print("50 dummy rows added successfully!")