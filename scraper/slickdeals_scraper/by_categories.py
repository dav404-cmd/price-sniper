from parsel import Selector
from datetime import datetime
import asyncio

async def go_to_page(page,xpath_structure,close_browser,category):
    url = f"https://slickdeals.net/deals/{category}/?page=1"
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector(xpath_structure["CARDS"], timeout=15000)
    except Exception as e:
        print(f"Navigation error: {e}")
        await close_browser()
        return

async def extract_category_deals(page, xpath_structure, to_float , category:str):
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
            "category" : category,
            "url": "https://slickdeals.net" + relative_url if relative_url else None,
            "scraped_at" : datetime.now().isoformat()
        })

    return extracted_deals


async def click_next_btn(page,next_btn_css):
    try:
        await page.wait_for_selector(next_btn_css, timeout=5000)
        next_button = await page.query_selector(next_btn_css)

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
