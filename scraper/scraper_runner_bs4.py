from scraper.slick_by_bs4.slick_bs4_scraper import SlickScraperBs4

def run_by_categories():
    scraper = SlickScraperBs4()
    scraper.scrape_by_categories(is_test=True, category="tech")

def run_by_search(is_test = True,query = "iphone"):
    scraper = SlickScraperBs4()
    scraper.scrape_by_search(is_test=is_test, query=query,max_pages=50)

if __name__ == "__main__":
    run_by_search()