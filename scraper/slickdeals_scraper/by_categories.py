from parsel import Selector
from datetime import datetime

async def go_to_page(page,xpath_structure,close_browser):
    url = "https://slickdeals.net/deals/tech/?page=1"
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector(xpath_structure["CARDS"], timeout=15000)
    except Exception as e:
        print(f"Navigation error: {e}")
        await close_browser()
        return

async def extract_category_deals(page, xpath_structure, to_float):
    html = await page.content()
    selector = Selector(text=html)

    deals = selector.css(xpath_structure["CARDS"])
    extracted_deals = []

    for deal in deals:
        relative_url = deal.css(xpath_structure["HREF"]).get()
        price = deal.css(xpath_structure["PRICE"]).get()
        cleaned_price = to_float(price)
        orig_price = deal.css(xpath_structure["ORIGINAL_PRICE"]).get()
        cleaned_orig_price = to_float(orig_price)

        extracted_deals.append({
            "title": deal.css(xpath_structure["TITLE"]).get(),
            "price": cleaned_price,
            "claimed_orig_price": cleaned_orig_price,
            "store": deal.css(xpath_structure["STORE"]).get(),
            "url": "https://slickdeals.net" + relative_url if relative_url else None,
            "scraped_at" : datetime.now().isoformat()
        })

    return extracted_deals
