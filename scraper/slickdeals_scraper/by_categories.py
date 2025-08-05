from parsel import Selector

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
            "title": deal.css(xpath_structure["TITLE"]).xpath("string()").get(),
            "price": cleaned_price,
            "claimed_orig_price": cleaned_orig_price,
            "store": deal.css(xpath_structure["STORE"]).xpath("string()").get(),
            "url": "https://slickdeals.net" + relative_url if relative_url else None
        })

    return extracted_deals
