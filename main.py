import pandas as pd
import streamlit as st
import sqlite3
from scraper.scraper_runner_bs4 import run_by_categories, run_by_search

st.set_page_config(layout="wide")
# todo : add Test mode toggle
test_mode = True
db_path = "database/listing.db"
db_path_test = "database/test.db"
use_file = db_path_test if test_mode else db_path

st.header("Price Sniper")
product = st.text_input("Product name..", "iphone")

# Run scraper button with a unique key
if st.button("Start Scraper", key="start_scraper"):
    run_by_search(is_test = True,query = product)  # todo : setup select box for run_by_test and run_by_category
    st.success("Scraper has finished running!")

conn = sqlite3.connect(use_file)
df = pd.read_sql_query("SELECT * FROM listings", conn)

tables = df[df["discount_percentage"] > 50][["title", "price", "claimed_orig_price", "discount_percentage"]]

st.subheader("Great deals.")
st.dataframe(tables,use_container_width=True, height=500)
conn.close()
