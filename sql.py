import sqlite3

class DataBase:
    def __init__(self,path):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            claimed_orig_price REAL,
            store TEXT,
            url TEXT
        )
        """)
        self.conn.commit()

    def insert_dicts(self, cards):
        self.cursor.executemany("""
            INSERT INTO listings (title, price, claimed_orig_price, store, url)
            VALUES (:title, :price, :claimed_orig_price, :store, :url)
        """, cards)
        self.conn.commit()


    def delete_first(self):
        self.cursor.execute("""
        DELETE FROM listings
        WHERE ROWID = (SELECT ROWID FROM listings ORDER BY ROWID ASC LIMIT 1)
        """)
        self.conn.commit()

    def delete_all(self):
        self.cursor.execute("DELETE FROM listings")
        self.conn.commit()
if __name__ == '__main__':
    sql = DataBase("test.db")
    sql.delete_all()
    sql.close()

