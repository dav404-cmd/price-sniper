from scraper.slickdeals_scraper.slick_scraper import SlickScraper
import asyncio

def run_by_categories():
    scraper = SlickScraper()
    asyncio.run(scraper.scrape_by_categories(is_test=True,category="tech"))

def run_by_search():
    scraper = SlickScraper()
    asyncio.run(scraper.scrape_by_search(is_test=True,query="iphone"))

if __name__ == '__main__':
 pass