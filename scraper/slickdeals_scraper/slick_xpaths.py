#for categories based scraping.

BY_CATEGORIES = {
    "CARDS": "li.bp-p-blueberryDealCard",
    "TITLE": "a.bp-c-card_title::text",
    "PRICE": "span.bp-p-dealCard_price::text",
    "STORE": "span.bp-c-card_subtitle::text",
    "ORIGINAL_PRICE": "span.bp-p-dealCard_originalPrice::text",
    "HREF": "a.bp-c-card_title::attr(href)",
    "NEXT_BTN" : "button.bp-c-pagination_next"
}
