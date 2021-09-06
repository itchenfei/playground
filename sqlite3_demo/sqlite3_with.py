import sqlite3
import time


class SQLite:
    def __init__(self, db='example.db'):
        self.db = db

    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


start = time.time()
with SQLite() as cur:
    print(time.time() - start)

    cur.execute(r"SELECT * FROM stocks ORDER BY price")
print(time.time() - start)
