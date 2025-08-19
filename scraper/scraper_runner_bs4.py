from scraper.slick_by_bs4.slick_bs4_scraper import SlickScraperBs4

def run_by_categories(is_test = True,category = "tech",max_page = 5):
    scraper = SlickScraperBs4()
    scraper.scrape_by_categories(is_test=is_test, category=category,max_pages = max_page)

def run_by_search(is_test = True,query = "iphone",max_pages = 5):
    scraper = SlickScraperBs4()
    scraper.scrape_by_search(is_test=is_test, query=query,max_pages=max_pages)

if __name__ == "__main__":
    run_by_search()