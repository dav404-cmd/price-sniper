from bs4 import BeautifulSoup
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}
class DeepScraper:
    """scrape a slickdeals deal page to get details and comments llm can use."""
    @staticmethod
    def get_html(url):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    @staticmethod
    def get_deal_details(html):
        soup = BeautifulSoup(html, "lxml")
        blocks = soup.select("div.dealDetailsRawHtml.dealDetailsTab__bodyHtml")

        cleaned = []
        for block in blocks:
            # Remove unwanted tags (links, tables, scripts, etc.)
            for tag in block.find_all(["a", "table", "script", "style", "img"]):
                tag.decompose()

            # Extract text, preserve newlines
            text = block.get_text(separator="\n", strip=True)

            # Clean multiple blank lines
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned.append("\n".join(lines))

        return cleaned

    @staticmethod
    def get_comments(html):
        soup = BeautifulSoup(html, "lxml")

        # Find all comment blocks
        comments = soup.select("div.commentsThreadedCommentV2")

        results = []
        for c in comments:

            text = c.get_text(" ", strip=True)

            results.append({
                "comment": text
            })
        return results

# tools/database_tools.py
"""TOOL 2"""
from manage_db.db_manager import PostgresDB  # your PostgresDB class

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
            ORDER BY discount_percentage DESC
            LIMIT %s
        """, (f"%{keyword}%", limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def search_under_price(self, keyword: str, max_price: float, limit: int = 10):
        """Search for deals under a given price."""
        self.cursor.execute("""
            SELECT * FROM listings
            WHERE title ILIKE %s AND price <= %s
            ORDER BY price ASC
            LIMIT %s
        """, (f"%{keyword}%", max_price, limit))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]



if __name__ == "__main__":
    url = "https://slickdeals.net/f/18164845-metro-by-t-mobile-iphone-13-128gb-125?src=SDSearchv3&attrsrc=Thread%3AExpired%3AFalse%7CSearch%3AType%3Anormal%7CSearch%3ASort%3Arelevance%7CSearch%3AHideExpired%3Atrue"
    tool = DeepScraper()
    html = tool.get_html(url)
    details = tool.get_deal_details(html)
    comments = tool.get_comments(html)
    print("==== DEAL COMMENTS ====")
    for c in comments[:5]:
        print(c)
    print("==== DEAL DETAILS ====")
    for d in details:
        print(d)

    print("==== search by title,url,underprice ====")

    tool2 = QuerySearcher()
    results = tool2.search_by_title("computer",limit=2)
    results2 = tool2.search_by_url(url)
    results3 = tool2.search_under_price("computer",500,limit=2)



    print("Results_title:", results)
    print("Results_url:", results2)
    print("Results_under_price:", results3)
