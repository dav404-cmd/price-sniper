from legacy.slickdeals_scraper.slick_scraper import SlickScraper

async def run_by_categories():
    scraper = SlickScraper()
    await scraper.scrape_by_categories(is_test=True, category="tech")

async def run_by_search(is_test=True, query="iphone"):
    scraper = SlickScraper()
    await scraper.scrape_by_search(is_test=is_test, query=query)