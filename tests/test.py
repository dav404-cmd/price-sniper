import pytest
from pathlib import Path
from scraper.slick_by_bs4.by_category_bs4 import extract_category_deals



# Example BY_SEARCH mapping from your scraper
BY_SEARCH = {
    "CARDS": ".dealCard",
    "TITLE": ".itemTitle",
    "PRICE": ".itemPrice",
    "ORIGINAL_PRICE": ".originalPrice",
    "STORE": ".dealStore",
    "TIME_STAMP": ".dealTimeStamp",
}

# Dummy float conversion
def to_float(val):
    try:
        return float(str(val).replace("$", "").replace(",", "").strip())
    except:
        return None

def test_extract_search_deals():
    _root = Path(__file__).parents[1].resolve()
    print(_root)

    html_path = Path(_root/"tests"/"test_component"/"example_deals.html")
    html = html_path.read_text()

    category = "Tech"
    results = extract_category_deals(to_float, html, BY_SEARCH, category)

    assert len(results) == 2

    first = results[0]
    assert first["title"].startswith("Costco Members")
    assert first["price"] == 150.0
    assert first["claimed_orig_price"] == 299.0
    assert first["discount"] == 149.0
    assert first["discount_percentage"] == pytest.approx(49.83, 0.01)
    assert first["store"] == "Costco Wholesale"
    assert first["category"] == "Tech"
    assert first["time_stamp"] == "2025-09-27 13:14"
    assert first["url"].startswith("https://slickdeals.net/f/")

