import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from pathlib import Path
import os

from scraper.slickdeals_scraper.slick_xpaths import BY_CATEGORIES
from scraper.slickdeals_scraper.by_categories import extract_category_deals
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

    async def click_next_btn(self, next_btn_css):
        try:
            await self.page.wait_for_selector(next_btn_css, timeout=5000)
            next_button = await self.page.query_selector(next_btn_css)

            # Get parent div
            parent = await next_button.evaluate_handle("node => node.parentElement")
            parent_class = await parent.get_property("className")
            parent_class_value = await parent_class.json_value()

            if "bp-c-pagination_ends--disabled" in parent_class_value:
                print("Next button is disabled based on parent class.")
                return False

            if next_button and await next_button.is_enabled() and await next_button.is_visible():
                await next_button.scroll_into_view_if_needed()
                await next_button.click()
                print("Navigated to next page.")
                await asyncio.sleep(2)
                return True
            else:
                print("Next button not available or disabled.")
                return False

        except Exception as e:
            print(f"Error while trying to click next: {e}")
            return False

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

    async def scraper(self,is_test = True):

        await self.start_browser()

        url = "https://slickdeals.net/deals/tech/?page=1"
        try:
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_selector(BY_CATEGORIES["CARDS"], timeout=15000)
        except Exception as e:
            print(f"Navigation error: {e}")
            await self.close_browser()
            return

        deals_lis = []
        deal_count = 0

        while deal_count < 60:

            new_deals = await extract_category_deals(self.page,BY_CATEGORIES,self.to_float)

            deal_count += len(new_deals)
            deals_lis.extend(new_deals)

            print(f"found {len(new_deals)} pages")

            has_next = await self.click_next_btn(BY_CATEGORIES["NEXT_BTN"])
            if not has_next:
                print("No more pages.")
                break

            await asyncio.sleep(2)

        print(deal_count)
        await self.close_browser()

        self.store_db(deals_lis,is_test = is_test)

        print(f"scraped {deal_count} listing")
        self.store_csv(deals_lis)

if __name__ == '__main__':
    scraper = SlickScraper()
    asyncio.run(scraper.scraper())
