#for categories based scraping.

BY_CATEGORIES = {
    "CARDS": "li.bp-p-blueberryDealCard",
    "TITLE": "a.bp-c-card_title::text",
    "PRICE": "span.bp-p-dealCard_price::text",
    "STORE": "span.bp-c-card_subtitle::text",
    "ORIGINAL_PRICE": "span.bp-p-dealCard_originalPrice::text",
    "HREF": "a.bp-c-card_title::attr(href)",
    "NEXT_BTN" : "button.bp-c-pagination_next",
    "TIME_STAMP" : "span.bp-p-blueberryDealCard_timestamp::text"
}

BY_SEARCH = {
    "CARDS": "a.dealCardListViewMobile__title.dealCardListViewMobile__title--underline",
    "HREF": "a.dealTitleLink::attr(href)",
    "PRICE": "span.price::text",
    "ORIGINAL_PRICE": "span.priceStrikeThrough::text",
    "TITLE": "a.dealTitleLink::text",
    "STORE": "span.dealMerchantName::text",
}