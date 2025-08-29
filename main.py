import pandas
import pandas as pd
import streamlit as st
import sqlite3
from scraper.scraper_runner_bs4 import run_by_categories, run_by_search
from data.data_cleaner.date_formating import time_ago
import json
import os
from datetime import datetime,timedelta

st.set_page_config(layout="wide")


db_path = "database/listing.db"
#CSV path that resets every run.(name is wrong.)
csv_path = "data/raw/cate_based_deals.csv"

#list of category.
category_data = "data/helper_data/slick_category.json"
with open(category_data,"r") as f:
    categories = json.load(f)

st.header("Price Sniper")

tab1,tab2,tab3 = st.tabs(["Scrape Data","Explore Data","Recent deals."])

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
        )
        start = st.button("Start scraper",key="category_scraper")
        if start and category:
            st.write(f"Scraping deals in category: {category}")
            with st.spinner("Scraper is running... please wait ⏳"):
                run_by_categories(category=category, max_page=50)
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
                run_by_search(query=query,max_pages = 50)

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
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM listings", conn)
        conn.close()

        tables = df[df["discount_percentage"] > 50][["title", "price", "claimed_orig_price", "discount_percentage", "url"]]
        st.subheader("Great deals (50%+ discount)")
        st.dataframe(tables, use_container_width=True)

        st.divider()

        st.subheader("Some other deals")
        all_table = df[["title", "price", "claimed_orig_price", "discount_percentage", "url"]].head(30)
        st.dataframe(all_table,use_container_width=True)


with tab3:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM listings", conn)
    conn.close()

    df["time_stamp"] = pd.to_datetime(df["time_stamp"])

    # Filter for >50% discount
    table1 = df[df["discount_percentage"] > 80][[
        "title", "price", "claimed_orig_price", "discount_percentage", "url", "time_stamp"
    ]]

    now = datetime.now()
    oldest_time = now - timedelta(days=30)

    # Keep rows between oldest_time and now
    table2 = table1[
        (table1["time_stamp"] >= oldest_time) &
        (table1["time_stamp"] <= now)
        ].copy()

    # Add post_date column using time_ago()
    table2["post_date"] = table2["time_stamp"].apply(time_ago)

    st.divider()

    st.subheader("Recent great deals . (80%+ discount.Only a month old)")
    #todo: switch the json formated data in to json like : title = title_ /n price = price_ format
    table2_json = [
        {
            "title": row["title"],
            "price": row["price"],
            "claimed original price" : row["claimed_orig_price"],
            "discount %" : row["discount_percentage"],
            "time stamp" : row["post_date"],
            "url" : row["url"]
        }
        for _, row in table2.iterrows()
    ]

    for item in table2_json:
        st.json(item)
