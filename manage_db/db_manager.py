import sqlite3
from utils.logger import get_logger

db_log = get_logger("DataBase_Manager")

class DataBase:
    def __init__(self,path,reset = False):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        if reset:
            db_log.critical(f"Reset=True will reset the {path} db")
            do_reset = input(f"DO YOU WISH TO PROCEED ? \nTYPE (YES I WANT TO DELETE DATA BASE) \nANYTHING ELSE WILL BE CONSIDERED NO. \nEnter answer : ")
            if do_reset == "YES I WANT TO DELETE DATA BASE":
                db_log.critical(f"Reset {path} DataBase")
                self.reset()
            else:
                db_log.critical(f"DataBase {path} was NOT deleted")

        self.create_table()

    def close(self):
        self.conn.close()

    def reset(self):
        self.cursor.execute("DROP TABLE IF EXISTS listings")
        self.conn.commit()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            claimed_orig_price REAL,
            discount REAL,
            discount_percentage REAL,
            store TEXT,
            category TEXT,
            time_stamp TEXT,
            url TEXT UNIQUE, --enforce uniqueness and remove dupes
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()
        self.cursor.execute("PRAGMA table_info(listings)")
        #columns = [col[1] for col in self.cursor.fetchall()]
        #db_log.info(f"Current columns in listings → {columns}")

    def insert_dicts(self, cards):
        db_log.info(f"Inserting {len(cards)} rows")
        self.cursor.executemany("""
            INSERT OR IGNORE INTO listings 
            (title, price, claimed_orig_price, discount, discount_percentage, store, category, time_stamp, url, scraped_at)
            VALUES (:title, :price, :claimed_orig_price, :discount, :discount_percentage, :store, :category, :time_stamp, :url, :scraped_at)
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

    def count_row(self):
        self.cursor.execute("SELECT COUNT(*) FROM listings")
        total_rows = self.cursor.fetchone()[0]
        db_log.info(f"Total rows in DB → {total_rows}")

    #searchers
    def find_by_url(self, url: str):
        self.cursor.execute("SELECT * FROM listings WHERE url = ?", (url,))
        row = self.cursor.fetchone()
        if row:
            col_names = [desc[0] for desc in self.cursor.description]
            return dict(zip(col_names, row))
        return None

    def search_by_title(self, keyword: str, limit: int = 10):
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title LIKE ?
            ORDER BY discount_percentage DESC
            LIMIT ?
        """, (f"%{keyword}%", limit))
        rows = self.cursor.fetchall()
        col_names = [desc[0] for desc in self.cursor.description]
        return [dict(zip(col_names, row)) for row in rows]

    def search_by_category(self, category: str, limit: int = 10):
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE category = ?
            ORDER BY time_stamp DESC
            LIMIT ?
        """, (category, limit))
        rows = self.cursor.fetchall()
        col_names = [desc[0] for desc in self.cursor.description]
        return [dict(zip(col_names, row)) for row in rows]






