#for categories based scraping.

BY_CATEGORIES = {
    "CARDS": "li.bp-p-blueberryDealCard",
    "TITLE": "a.bp-c-card_title",
    "PRICE": "span.bp-p-dealCard_price",
    "STORE": "span.bp-c-card_subtitle",
    "ORIGINAL_PRICE": "span.bp-p-dealCard_originalPrice",
    "HREF": "a.bp-c-card_title::attr(href)",
    "NEXT_BTN" : "button.bp-c-pagination_next",
    "TIME_STAMP" : "span.bp-p-blueberryDealCard_timestamp"
}

BY_SEARCH = {
    "CARDS": "div.dealCardListView",
    "TITLE": "a.dealCardListView__title--underline",
    "PRICE": "span.dealCardListView__finalPrice",
    "ORIGINAL_PRICE": "span.dealCardListView__listPrice",
    "STORE": "div.dealCardListView__store",
    "TIME_STAMP" : "span.slickdealsTimestamp"
}