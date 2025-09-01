import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from utils.logger import get_logger
import os
from dotenv import load_dotenv
db_log = get_logger("Postgres_Manager")

load_dotenv()

class PostgresDB:
    def __init__(self, dbname="dealsdb",reset=False):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        if reset:
            db_log.critical(f"Reset=True will reset the {dbname} database")
            do_reset = input(
                "DO YOU WISH TO PROCEED ?\n"
                "TYPE (YES I WANT TO DELETE DATA BASE)\n"
                "ANYTHING ELSE WILL BE CONSIDERED NO.\nEnter answer : "
            )
            if do_reset == "YES I WANT TO DELETE DATA BASE":
                db_log.critical(f"Reset {dbname} database")
                self.reset()
            else:
                db_log.critical(f"Database {dbname} was NOT deleted")

        self.create_table()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def reset(self):
        self.cursor.execute("DROP TABLE IF EXISTS listings")
        self.conn.commit()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price DOUBLE PRECISION,
            claimed_orig_price DOUBLE PRECISION,
            discount DOUBLE PRECISION,
            discount_percentage DOUBLE PRECISION,
            store TEXT,
            category TEXT,
            time_stamp TIMESTAMP,
            url TEXT UNIQUE, -- enforce uniqueness
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()
        db_log.info("Ensure Table Exists.")

    def insert_dicts(self, cards):
        db_log.info(f"Inserting {len(cards)} rows")
        query = """
            INSERT INTO listings
            (title, price, claimed_orig_price, discount, discount_percentage, store, category, time_stamp, url, scraped_at)
            VALUES %s
            ON CONFLICT (url) DO NOTHING
        """
        values = [
            (
                card.get("title"),
                card.get("price"),
                card.get("claimed_orig_price"),
                card.get("discount"),
                card.get("discount_percentage"),
                card.get("store"),
                card.get("category"),
                card.get("time_stamp"),
                card.get("url"),
                card.get("scraped_at"),
            )
            for card in cards
        ]
        execute_values(self.cursor, query, values)
        self.conn.commit()

    def delete_first(self):
        self.cursor.execute("""
        DELETE FROM listings
        WHERE id = (
            SELECT id FROM listings ORDER BY id ASC LIMIT 1
        )
        """)
        self.conn.commit()

    def delete_all(self):
        self.cursor.execute("DELETE FROM listings")
        self.conn.commit()

    def count_row(self):
        self.cursor.execute("SELECT COUNT(*) FROM listings")
        total_rows = self.cursor.fetchone()["count"]
        db_log.info(f"Total rows in DB → {total_rows}")

    # Searchers

    def show_all(self, readable=False):
        self.cursor.execute("SELECT * FROM listings")
        rows = self.cursor.fetchall()

        # Convert RealDictCursor rows to normal dicts
        rows = [dict(row) for row in rows]

        if readable:
            for row in rows:
                # Format scraped_at to a readable "time ago" if you want
                scraped_at = row.get("scraped_at")
                print(
                    f"{row['id']:3} | {row['title'][:40]:40} | ${row['price']:8.2f} | {row['discount_percentage']:5.1f}% | {row['scraped_at']} | {row['time_stamp']} | {row['url']}")

        return rows

    def find_by_url(self, url: str):
        self.cursor.execute("SELECT * FROM listings WHERE url = %s", (url,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def search_by_title(self, keyword: str, limit: int = 10):
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s
            ORDER BY discount_percentage DESC
            LIMIT %s
        """, (f"%{keyword}%", limit))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def search_by_category(self, category: str, limit: int = 10):
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE category = %s
            ORDER BY time_stamp DESC
            LIMIT %s
        """, (category, limit))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

if __name__ == "__main__":
    db = PostgresDB()

    all1 = db.show_all(readable=True)

    db.close()
