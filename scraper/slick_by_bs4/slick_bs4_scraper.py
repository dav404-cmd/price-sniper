import requests
import pandas as pd
from pathlib import Path
import os
import time

from scraper.slickdeals_scraper.slick_xpaths import BY_CATEGORIES, BY_SEARCH
from scraper.slick_by_bs4.by_category_bs4 import extract_category_deals
from scraper.slick_by_bs4.by_search_bs4 import extract_search_deals

from manage_db.db_manager import DataBase

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}

class SlickScraperBs4:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]

    # -------- Helpers --------
    @staticmethod
    def to_float(value):
        try:
            return float(str(value).replace("$", "").replace(",", "").strip())
        except (ValueError, TypeError, AttributeError):
            return None

    def get_csv_path(self) -> Path:
        csv_folder = self.project_root / "data" / "raw"
        output_csv = csv_folder / "cate_based_deals.csv"
        return output_csv

    def get_db_path(self, is_test) -> Path:
        database_path = self.project_root / "database"
        db_path = database_path / "listing.db"
        test_db_path = database_path / "test.db"
        return test_db_path if is_test else db_path

    def store_csv(self, deals_lis):
        output_file = self.get_csv_path()
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df = pd.DataFrame(deals_lis)
        df.to_csv(output_file, index=False)
        print(f"CSV saved → {output_file}")

    def store_db(self, deals_lis, is_test):
        output_db = self.get_db_path(is_test=is_test)
        sql = DataBase(output_db, is_test=is_test)
        if deals_lis:
            sql.insert_dicts(deals_lis)
            sql.close()
        print(f"Database saved → {output_db}")
    @staticmethod
    def get_page_html(url: str) -> str | None:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    # -------- Main Runners --------
    def scrape_by_categories(self, is_test=True, category="tech"):
        base_url = f"https://slickdeals.net/deals/{category}/?page=1"
        deals_lis, deal_count = [], 0
        url = base_url

        while url and deal_count < 120:
            print(f"Scraping: {url}")
            html = self.get_page_html(url)
            if not html:
                break

            new_deals = extract_category_deals(self.to_float,html, BY_CATEGORIES, category)
            deal_count += len(new_deals)
            deals_lis.extend(new_deals)

            print(f"→ Found {len(new_deals)} deals on this page")

            page_num = int(url.split("page=")[-1]) + 1
            url = f"https://slickdeals.net/deals/{category}/?page={page_num}"

            time.sleep(2)

        print(f"* Scraped {deal_count} listings")
        self.store_db(deals_lis, is_test=is_test)
        self.store_csv(deals_lis)

    def scrape_by_search(self, is_test=True, query="iphone", total_pages=5):
        query_clean = query.replace(" ", "+")
        base_url = f"https://slickdeals.net/search?q={query_clean}&filters[display][]=hideExpired&page="

        deals_lis, deal_count = [], 0

        for page_num in range(1, total_pages + 1):
            url = base_url + str(page_num)
            print(f"Scraping page {page_num}: {url}")
            html = self.get_page_html(url)
            if not html:
                continue

            new_deals = extract_search_deals(self.to_float,html, BY_SEARCH)
            deal_count += len(new_deals)
            deals_lis.extend(new_deals)

            print(f"→ Found {len(new_deals)} deals on page {page_num}")
            time.sleep(2)

        print(f"* Total scraped listings: {deal_count}")
        self.store_db(deals_lis, is_test=is_test)
        self.store_csv(deals_lis)


# -------- Entry Points --------
def run_by_categories():
    scraper = SlickScraperBs4()
    scraper.scrape_by_categories(is_test=True, category="tech")

def run_by_search():
    scraper = SlickScraperBs4()
    scraper.scrape_by_search(is_test=True, query="iphone")

if __name__ == "__main__":
    run_by_categories()
