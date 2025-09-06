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
        #currently only scraped first page of comments.
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




