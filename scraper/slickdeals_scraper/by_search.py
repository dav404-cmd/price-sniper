from parsel import Selector
from datetime import datetime

async def extract_search_deals(page, xpath_structure, to_float):
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

        if cleaned_price is None or cleaned_orig_price is None or cleaned_orig_price == 0:
            continue
        discount = cleaned_orig_price - cleaned_price
        discount_percentage = (discount/cleaned_orig_price)*100
        formatted = f"{discount_percentage:.2f}"
        float_discount = to_float(formatted)

        extracted_deals.append({
            "title": deal.css(xpath_structure["TITLE"]).get(),
            "price": cleaned_price,
            "claimed_orig_price": cleaned_orig_price,
            "discount_percentage": float_discount,
            "store": deal.css(xpath_structure["STORE"]).get(),
            "category" : None,
            "time_stamp" : None,
            "url": "https://slickdeals.net" + relative_url if relative_url else None,
            "scraped_at" : datetime.now().isoformat()
        })

    return extracted_deals
