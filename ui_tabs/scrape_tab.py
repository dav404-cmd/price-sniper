import streamlit as st
import pandas as pd
import os
from scraper.scraper_runner_bs4 import run_by_categories, run_by_search
import json


CSV_PATH = "data/raw/cate_based_deals.csv"


def _load_scraped_table():
    """Helper: Load scraped CSV into session state"""
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        df = pd.read_csv(CSV_PATH)
        st.session_state.setdefault("scraped_table", df)
    elif os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) <= 0:
        st.warning("NO data found.")

@st.cache_data
def _load_category_data():
    category_data = "data/helper_data/slick_category.json"
    with open(category_data, "r") as f:
        return json.load(f)

def render():
    mode = st.radio("**Choose scraping mode:**", ["Scrape by Category", "Scrape by Search"])
    st.write("")

    if mode == "Scrape by Category":
        categories = _load_category_data()

        category = st.selectbox(
            "Search for a category or keyword:",
            options=categories,
            index=None,
            placeholder="Start typing...",
            key="autocomplete_input",
        )
        start = st.button("Start scraper", key="category_scraper")

        if start and category:
            st.write(f"Scraping deals in category: {category}")
            with st.spinner("Scraper is running... please wait ⏳"):
                run_by_categories(category, max_page=50)
                st.success("Scraper has finished running!")

            _load_scraped_table()

        if "scraped_table" in st.session_state:
            st.subheader("Scraped Data.")
            st.dataframe(st.session_state["scraped_table"], use_container_width=True)

    elif mode == "Scrape by Search":
        query = st.text_input("Enter search keyword:")
        start = st.button("Start scraper", key="search_scraper")

        if start and query:
            with st.spinner(f"Scraper is running... please wait ⏳.\nSearching for :**{query}**"):
                run_by_search(query, max_pages=50)
                st.success("Scraper has finished running!")
            _load_scraped_table()

        if "scraped_table" in st.session_state:
            st.subheader("Scraped Data.")
            st.dataframe(st.session_state["scraped_table"], use_container_width=True)



