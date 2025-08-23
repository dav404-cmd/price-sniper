import pandas
import pandas as pd
import streamlit as st
import sqlite3
from scraper.scraper_runner_bs4 import run_by_categories, run_by_search
import json
import os

st.set_page_config(layout="wide")

# todo : add Test mode toggle

test_mode = True
db_path = "database/listing.db"
db_path_test = "database/test.db"
use_file = db_path_test if test_mode else db_path

#CSV path that resets every run.(name is wrong.)
csv_path = "data/raw/cate_based_deals.csv"

#list of category.
category_data = "data/helper_data/slick_category.json"
with open(category_data,"r") as f:
    categories = json.load(f)

st.header("Price Sniper")

tab1,tab2 = st.tabs(["Scrape Data","Explore Data"])

st.divider()

with tab1:
    mode = st.radio("**Choose scraping mode:**", ["Scrape by Category", "Scrape by Search"])
    st.write("")
    if mode == "Scrape by Category":
        category = st.selectbox(
            "Search for a category or keyword:",
            options=categories,
            index=None,
            placeholder="Start typing...",
            key="autocomplete_input",
            # editable=True is now default in recent Streamlit versions
        )
        start = st.button("Start scraper",key="category_scraper")
        if start and category:
            st.write(f"Scraping deals in category: {category}")
            with st.spinner("Scraper is running... please wait ⏳"):
                run_by_categories(is_test=True, category=category, max_page=5)
                st.success("Scraper has finished running!")

            # Load and cache scraped data
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                df = pandas.read_csv(csv_path)
                st.session_state["scraped_table"] = df

        # Display cached table if available
        if "scraped_table" in st.session_state:
            st.subheader("Scraped Data.")
            st.dataframe(st.session_state["scraped_table"], use_container_width=True)

    elif mode == "Scrape by Search":
        query = st.text_input("Enter search keyword:")
        start = st.button("Start scraper",key="search_scraper")
        if start and query:
            with st.spinner(f"Scraper is running... please wait ⏳.\nSearching for :**{query}**"):
                run_by_search(is_test=True, query=query,max_pages = 5)

                st.success("Scraper has finished running!")

                # Load and cache scraped data
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                df = pandas.read_csv(csv_path)
                st.session_state["scraped_table"] = df

            # Display cached table if available
        if "scraped_table" in st.session_state:
            st.subheader("Scraped Data.")
            st.dataframe(st.session_state["scraped_table"], use_container_width=True)

with tab2:
    if st.button("Show or Refresh Table", key="refresh_table"):
        conn = sqlite3.connect(use_file)
        df = pd.read_sql_query("SELECT * FROM listings", conn)
        conn.close()

        tables = df[df["discount_percentage"] > 50][["title", "price", "claimed_orig_price", "discount_percentage", "url"]]
        st.subheader("Great deals (50%+ discount)")
        st.dataframe(tables, use_container_width=True)

        st.divider()

        st.subheader("Some other deals")
        all_table = df[["title", "price", "claimed_orig_price", "discount_percentage", "url"]].head(30)
        st.dataframe(all_table,use_container_width=True)
