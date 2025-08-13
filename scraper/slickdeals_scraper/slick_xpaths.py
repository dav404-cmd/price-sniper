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
    "CARDS": "div.dealCardListView",
    "TITLE": "a.dealCardListView__title--underline::text",
    "PRICE": "span.dealCardListView__finalPrice::text",
    "ORIGINAL_PRICE": "span.dealCardListView__listPrice::text",
    "STORE": "div.dealCardListView__store::text",
    "HREF": "a.dealCardListView__title--underline::attr(href)",
    "NEXT_BTN" : "a.slickdealsPagination__pageIcon"

}