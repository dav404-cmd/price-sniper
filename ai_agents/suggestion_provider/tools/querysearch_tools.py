from manage_db.db_manager import PostgresDB
from datetime import datetime,timedelta

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
            ORDER BY discount_percentage ASC,time_stamp DESC
            LIMIT %s
        """, (f"%{keyword}%", limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def search_under_price(self, keyword: str, max_price: float, limit: int = 10):
        """Search for deals under a given price."""
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s AND price <= %s
            ORDER BY price DESC,time_stamp DESC
            LIMIT %s
        """, (f"%{keyword}%", max_price, limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def search_closest_price(self, keyword: str, price: float, limit: int = 10):
        """Search for deals closest to a given price."""
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s
            ORDER BY ABS(price - %s),time_stamp DESC
            LIMIT %s
        """, (f"%{keyword}%", price, limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def search_recent_deals(self,keyword: str , days_ago: int , limit:int = 10):
        """Search for recent deals with title"""
        cutoff_date = datetime.now() - timedelta(days=days_ago)
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s AND time_stamp >= %s
            ORDER BY time_stamp DESC
            LIMIT %s 
        """,(f"%{keyword}%",cutoff_date,limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

if __name__ == "__main__":

    # ----TESTS----

    url = "https://slickdeals.net/f/18164845-metro-by-t-mobile-iphone-13-128gb-125?src=SDSearchv3&attrsrc=Thread%3AExpired%3AFalse%7CSearch%3AType%3Anormal%7CSearch%3ASort%3Arelevance%7CSearch%3AHideExpired%3Atrue"
    tool = QuerySearcher()
    title_results = tool.search_by_title("computer",limit=2)
    url_results = tool.search_by_url(url)
    under_price_results = tool.search_under_price("computer",max_price=700,limit=2)
    closest_price_results = tool.search_closest_price("iphone",price=600,limit=2)
    recent_deals = tool.search_recent_deals("iphone",14,10)

    import pprint

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(title_results)
    print("\n"+30*"-title_results-"+"\n")
    pp.pprint(url_results)
    print("\n" + 30 * "-url_results-" + "\n")
    pp.pprint(under_price_results)
    print("\n" + 30 * "-under_results-" + "\n")
    pp.pprint(closest_price_results)
    print("\n" + 30 * "-closest_price-" + "\n")
    pp.pprint(recent_deals)

