from bs4 import BeautifulSoup
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}
class DeepScraper:
    def get_html(self,url):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_deal_details(self,html):
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


    def get_comments(self,html):
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
from manage_db.db_manager import DataBase
from pathlib import Path
root = Path(__file__).parents[2].resolve()
db_path = root / "database" / "listing.db"
print(f"path {db_path}")

class QuerySearcher:
    def __init__(self):
        self.db = DataBase(db_path)
        self.cursor = self.db.cursor

    def search_by_url(self,urls: str):
        """Search the listings table for a specific URL."""
        rows = self.db.cursor.execute(
            "SELECT * FROM listings WHERE url = ?", (urls,)
        ).fetchall()
        return [dict(zip([c[0] for c in self.db.cursor.description], row)) for row in rows]

    def search_by_title(self,keyword: str, limit: int = 10):
        """Search listings by keyword in title."""
        self.cursor.execute("""
                    SELECT * FROM listings
                    WHERE title LIKE ?
                    ORDER BY discount_percentage DESC
                    LIMIT ?
                """, (f"%{keyword}%", limit))
        rows = self.cursor.fetchall()
        col_names = [desc[0] for desc in self.cursor.description]
        return [dict(zip(col_names, row)) for row in rows]

    def search_under_price(self,keyword:str,max_price: float, limit: int = 10):
        """Search for deals under a given price."""
        rows = self.db.cursor.execute(
            "SELECT * FROM listings WHERE LOWER(title) LIKE LOWER(?) AND price <= ? ORDER BY price ASC LIMIT ?",
            (f"%{keyword}%",max_price, limit)
        ).fetchall()
        return [dict(zip([c[0] for c in self.db.cursor.description], row)) for row in rows]



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

    print("==== search by url ====")

    tool2 = QuerySearcher()
    results = tool2.search_under_price("computer",500,5)
    print("Results:", results)