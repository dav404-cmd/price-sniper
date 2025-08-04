import asyncio
from time import sleep

import pandas as pd
from parsel import Selector
from playwright.async_api import async_playwright
from pathlib import Path
import os

from scraper.slickdeals_scraper.slick_xpaths import CARDS,TITLE,PRICE,STORE,ORIGINAL_PRICE,HREF,NEXT_BTN

class SlickScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
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

    async def scraper(self):
        project_root = Path(__file__).resolve().parents[2]
        print(f"project_root : {project_root}")

        output_file = project_root / 'data' / 'raw' / 'cate_based_deals.csv'
        os.makedirs(os.path.dirname(output_file),exist_ok=True)

        await self.start_browser()

        url = "https://slickdeals.net/deals/tech/?page=1"
        try:
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_selector(CARDS, timeout=15000)
        except Exception as e:
            print(f"Navigation error: {e}")
            await self.close_browser()
            return

        deals_lis = []
        deal_count = 0
        while True:

            html = await self.page.content()
            selector = Selector(text=html)

            deals = selector.css(CARDS)
            for deal in deals:
                relative_url = deal.css(HREF).get()
                deals_lis.append({
                    "title" : deal.css(TITLE).get(),
                    "price" : deal.css(PRICE).get(),
                    "claimed_orig_price": deal.css(ORIGINAL_PRICE).get(),
                    "store" : deal.css(STORE).get(),
                    "url" : "https://slickdeals.net" + relative_url if relative_url else None
                })
            deal_count += len(deals)
            print(f"found {len(deals)} pages")

            has_next = await self.click_next_btn(NEXT_BTN)
            if not has_next:
                print("No more pages.")
                break

            await asyncio.sleep(2)

        print(deal_count)
        await self.close_browser()

        df = pd.DataFrame(deals_lis)
        df.to_csv(output_file,index=False)
        print(f"scraped {deal_count} deals")
        print(f"output path : {output_file}")

if __name__ == '__main__':
    scraper = SlickScraper()
    asyncio.run(scraper.scraper())
