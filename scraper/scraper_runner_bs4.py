from scraper.slick_by_bs4.slick_bs4_scraper import SlickScraperBs4

def run_by_categories(category = "tech",max_page = 5):
    scraper = SlickScraperBs4()
    scraper.scrape_by_categories(category=category,max_pages = max_page)

def run_by_search(query = "iphone",max_pages = 50):
    scraper = SlickScraperBs4()
    scraper.scrape_by_search(query=query,max_pages=max_pages)

if __name__ == "__main__":
    run_by_categories()