from manage_db.db_manager import PostgresDB

class QuerySearcher:
    def __init__(self):
        self.db = PostgresDB()
        self.cursor = self.db.cursor

    def search_by_url(self, urls: str):
        """Search the listings table for a specific URL."""
        self.cursor.execute(
            "SELECT * FROM listings WHERE url = %s", (urls,)
        )
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def search_by_title(self, keyword: str, limit: int = 10):
        """Search listings by keyword in title."""
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s
            ORDER BY discount_percentage ASC
            LIMIT %s
        """, (f"%{keyword}%", limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def search_under_price(self, keyword: str, max_price: float, limit: int = 10):
        """Search for deals under a given price."""
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s AND price <= %s
            ORDER BY price DESC
            LIMIT %s
        """, (f"%{keyword}%", max_price, limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

if __name__ == "__main__":
    url = "https://slickdeals.net/f/18164845-metro-by-t-mobile-iphone-13-128gb-125?src=SDSearchv3&attrsrc=Thread%3AExpired%3AFalse%7CSearch%3AType%3Anormal%7CSearch%3ASort%3Arelevance%7CSearch%3AHideExpired%3Atrue"
    tool = QuerySearcher()
    title_results = tool.search_by_title("computer",limit=2)
    url_results = tool.search_by_url(url)
    under_price_results = tool.search_under_price("computer",max_price=700,limit=2)
    print(f"result_title : {title_results}")
    print(f"result_url : {url_results}")
    print(f"result_under_price : {under_price_results}")
