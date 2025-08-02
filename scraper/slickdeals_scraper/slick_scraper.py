import asyncio

import pandas as pd
from parsel import Selector
from playwright.async_api import async_playwright
from pathlib import Path
import os

from scraper.slickdeals_scraper.slick_xpaths import CARDS,TITLE,PRICE,STORE,ORIGINAL_PRICE,HREF

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

        html = await self.page.content()
        selector = Selector(text=html)

        jobs = []

        deals = selector.css(CARDS)
        for deal in deals:
            relative_url = deal.css(HREF).get()
            jobs.append({
                "title" : deal.css(TITLE).get(),
                "price" : deal.css(PRICE).get(),
                "claimed_orig_price": deal.css(ORIGINAL_PRICE).get(),
                "store" : deal.css(STORE).get(),
                "url" : "https://slickdeals.net" + relative_url if relative_url else None
            })

        print(len(deals))
        await self.close_browser()

        df = pd.DataFrame(jobs)
        df.to_csv(output_file,index=False)
        print(f"scraped {len(deals)} deals")
        print(f"output path : {output_file}")

if __name__ == '__main__':
    scraper = SlickScraper()
    asyncio.run(scraper.scraper())
