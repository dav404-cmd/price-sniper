import sqlite3

class DataBase:
    def __init__(self,path,is_test):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        if is_test:
            self.reset()
        self.create_table()

    def close(self):
        self.conn.close()

    def reset(self):
        self.cursor.execute("DROP TABLE IF EXISTS listings")
        self.conn.commit()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            claimed_orig_price REAL,
            discount_percentage REAL,
            store TEXT,
            category TEXT,
            time_stamp TEXT,
            url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def insert_dicts(self, cards):
        print("Inserting", len(cards), "rows")
        self.cursor.executemany("""
            INSERT INTO listings (title, price, claimed_orig_price, discount_percentage, store, category, time_stamp, url, scraped_at)
            VALUES (:title, :price, :claimed_orig_price, :discount_percentage, :store, :category, :time_stamp, :url, :scraped_at)
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



