import sqlite3

class DataBase:
    def __init__(self,path):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def store_db(self):
        self.cursor.execute("""
        INSERT INTO listings (title, price, date_scraped)
        VALUES ('Used Laptop', 450.0, '2025-08-03')
        """)

        self.conn.commit()

    def delete_data(self):
        self.cursor.execute("""
        DELETE FROM listings
        WHERE ROWID = (SELECT ROWID FROM listings ORDER BY ROWID ASC LIMIT 1)
        """)
        self.conn.commit()


sql_db = DataBase("test.db")
sql_db.delete_data()
sql_db.close()
