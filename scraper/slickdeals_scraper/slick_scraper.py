import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from pathlib import Path
import os

from scraper.slickdeals_scraper.slick_xpaths import BY_CATEGORIES , BY_SEARCH
from scraper.slickdeals_scraper.by_categories import extract_category_deals , go_to_page , click_next_btn
from scraper.slickdeals_scraper.by_search import extract_search_deals
from manage_db.db_manager import DataBase

class SlickScraper:
    def __init__(self,project_root : Path = None):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.project_root = project_root or Path(__file__).resolve().parents[2]

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @staticmethod
    def to_float(value):
        try:
            return float(str(value).replace("$", "").replace(",", "").strip())
        except (ValueError, TypeError):
            return None

    #[data storing]
    def get_csv_path(self) -> Path:
        csv_folder = self.project_root / 'data' / 'raw'
        output_csv = csv_folder / 'cate_based_deals.csv'
        return output_csv

    def get_db_path(self,is_test) -> Path:
        database_path = self.project_root / "database"

        db_path = database_path / "listing.db"
        test_db_path = database_path / "test.db"

        return test_db_path if is_test else db_path

    def store_csv(self,deals_lis):
        output_file = self.get_csv_path()
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df = pd.DataFrame(deals_lis)
        df.to_csv(output_file, index=False)
        print(f"output path : {output_file}")

    def store_db(self,deals_lis,is_test):
        output_db = self.get_db_path(is_test=is_test)
        sql = DataBase(output_db, is_test=is_test)
        if deals_lis:
            sql.insert_dicts(deals_lis)
            sql.close()
        print(f"database : {output_db}")

    async def scrape_by_categories(self,is_test = True,category = "tech"):

        await self.start_browser()

        await go_to_page(page=self.page,xpath_structure=BY_CATEGORIES,close_browser=self.close_browser ,category=category)

        deals_lis = []
        deal_count = 0

        while deal_count < 120:

            new_deals = await extract_category_deals(self.page,BY_CATEGORIES,self.to_float,category = category)

            deal_count += len(new_deals)
            deals_lis.extend(new_deals)

            print(f"found {len(new_deals)} pages")

            has_next = await click_next_btn(self.page,next_btn_css=BY_CATEGORIES["NEXT_BTN"])
            if not has_next:
                print("No more pages.")
                break

            await asyncio.sleep(2)

        print(deal_count)
        await self.close_browser()

        self.store_db(deals_lis,is_test = is_test)

        print(f"scraped {deal_count} listing")
        self.store_csv(deals_lis)

    async def scrape_by_search(self, is_test=True, query="iphone", total_pages=5):
        await self.start_browser()

        query_clean = query.replace(" ", "+")
        base_url = f"https://slickdeals.net/search?q={query_clean}&filters[display][]=hideExpired&page="

        deals_lis = []
        deal_count = 0

        for page_num in range(1, total_pages + 1):
            url = base_url + str(page_num)
            print(f"Scraping page {page_num}: {url}")
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=90000)
                cards = await self.page.query_selector(BY_SEARCH["CARDS"])
                if not cards:
                    print("No card found — stopping scraper.")
                    await self.close_browser()
                    return
                await asyncio.sleep(0.6)

            except Exception as e:
                print(f"Error loading page {page_num}: {e}")
                continue  # skip to next page, browser stays alive

            new_deals = await extract_search_deals(self.page, BY_SEARCH, self.to_float)
            deal_count += len(new_deals)
            deals_lis.extend(new_deals)

            print(f"Found {len(new_deals)} deals on page {page_num}")
            await asyncio.sleep(2)

        await self.close_browser()

        print(f"Total scraped listings: {deal_count}")
        self.store_db(deals_lis, is_test=is_test)
        self.store_csv(deals_lis)


def run_by_categories():
    scraper = SlickScraper()
    asyncio.run(scraper.scrape_by_categories(is_test=True,category="tech"))

def run_by_search():
    scraper = SlickScraper()
    asyncio.run(scraper.scrape_by_search(is_test=True,query="iphone"))

if __name__ == '__main__':
    run_by_categories()