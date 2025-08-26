import requests
import pandas as pd
from pathlib import Path
import os
import time

from scraper.slick_by_bs4.slick_xpaths import BY_CATEGORIES, BY_SEARCH
from scraper.slick_by_bs4.by_category_bs4 import extract_category_deals
from scraper.slick_by_bs4.by_search_bs4 import extract_search_deals
from utils.logger import get_logger
from support_llm.category_filler import fill_category

slick_log = get_logger("Slick_bs4_scraper")

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
        slick_log.info(f"CSV saved → {output_file}")

    def store_db(self, deals_lis,is_test = False):
        output_db = self.get_db_path(is_test=is_test)
        sql = DataBase(output_db)
        if deals_lis:
            sql.insert_dicts(deals_lis)
            sql.close()
        slick_log.info(f"Database saved → {output_db}")

    @staticmethod
    def get_page_html(url: str) -> str | None:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            slick_log.error(f"Error fetching {url}: {e}")
            return None

    # -------- Main Runners --------
    def scrape_by_categories(self,category="tech", max_pages=5):
        base_url = f"https://slickdeals.net/deals/{category}/?page=1"
        deals_lis, deal_count = [], 0
        url = base_url
        page_num = 1

        while url and page_num <= max_pages:
            slick_log.info(f"Scraping: {url}")
            html = self.get_page_html(url)
            if not html:
                break

            new_deals = extract_category_deals(self.to_float, html, BY_CATEGORIES, category)
            deal_count += len(new_deals)
            deals_lis.extend(new_deals)
            if len(new_deals) == 0:
                break

            slick_log.info(f"→ Found {len(new_deals)} deals on this page")

            page_num += 1
            url = f"https://slickdeals.net/deals/{category}/?page={page_num}"

            time.sleep(2)

        slick_log.info(f"* Scraped {deal_count} listings")
        self.store_db(deals_lis)
        self.store_csv(deals_lis)

    def scrape_by_search(self,query="iphone", max_pages=50):

        """FIll category using query"""
        category = fill_category(query)
        slick_log.info(f"Category filled with {category}")

        query_clean = query.replace(" ", "+")
        base_url = f"https://slickdeals.net/search?q={query_clean}&filters[display][]=hideExpired&page="

        deals_lis, deal_count = [], 0
        page_num = 1

        while page_num <= max_pages:  # failsafe max_pages
            url = base_url + str(page_num)
            slick_log.info(f"Scraping page {page_num}: {url}")
            html = self.get_page_html(url)
            if not html:
                break

            new_deals = extract_search_deals(self.to_float, html, BY_SEARCH,category = category)
            if not new_deals:  # ^ Stop if no deals are found
                slick_log.info("No more deals found, stopping.")
                break

            deal_count += len(new_deals)
            deals_lis.extend(new_deals)
            slick_log.info(f"→ Found {len(new_deals)} deals on page {page_num}")

            page_num += 1
            time.sleep(2)

        slick_log.info(f"* Total scraped listings: {deal_count}")
        self.store_db(deals_lis)
        self.store_csv(deals_lis)


# -------- Entry Points --------
def run_by_categories():
    scraper = SlickScraperBs4()
    scraper.scrape_by_categories(category="tech")

def run_by_search():
    scraper = SlickScraperBs4()
    scraper.scrape_by_search(query="iphone")

if __name__ == "__main__":
    run_by_categories()
