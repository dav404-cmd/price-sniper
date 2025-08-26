from bs4 import BeautifulSoup
from datetime import datetime
from data.data_cleaner.date_formating import normalize_scraped_date

def extract_search_deals(to_float, html: str, xpath_structure: dict, category):
    soup = BeautifulSoup(html, "lxml")
    deals = soup.select(xpath_structure["CARDS"])
    extracted = []

    for deal in deals:
        # Title
        title_tag = deal.select_one(xpath_structure["TITLE"])
        title = title_tag.get_text(strip=True) if title_tag else None

        # URL
        relative_url = title_tag.get("href") if title_tag else None

        # Price
        price_tag = deal.select_one(xpath_structure["PRICE"])
        cleaned_price = to_float(price_tag.get_text()) if price_tag else None

        # Original Price
        orig_price_tag = deal.select_one(xpath_structure["ORIGINAL_PRICE"])
        cleaned_orig_price = to_float(orig_price_tag.get_text()) if orig_price_tag else None

        if cleaned_price is None or cleaned_orig_price is None or cleaned_orig_price == 0:
            continue

        discount = cleaned_orig_price - cleaned_price
        discount_percentage = (discount / cleaned_orig_price) * 100
        float_discount = float(f"{discount_percentage:.2f}")

        time_stamp = (
            deal.select_one(xpath_structure["TIME_STAMP"]).get_text(strip=True)
            if deal.select_one(xpath_structure["TIME_STAMP"]) else None)
        formated_time_stamp = normalize_scraped_date(time_stamp)

        extracted.append({
            "title": title,
            "price": cleaned_price,
            "claimed_orig_price": cleaned_orig_price,
            "discount_percentage": float_discount,
            "discount": discount,
            "store": (deal.select_one(xpath_structure["STORE"]).get_text(strip=True)
                      if deal.select_one(xpath_structure["STORE"]) else None),
            "category": category,
            "time_stamp": formated_time_stamp,
            "url": "https://slickdeals.net" + relative_url if relative_url else None,
            "scraped_at": datetime.now()
        })

    return extracted