import streamlit as st
import pandas as pd
from datetime import datetime

from ai_agents.suggestion_provider.tools.querysearch_tools import QuerySearcher

def render_deals(df:pd.DataFrame):
    for _, row in df.iterrows():
        st.markdown(f"""
        🛍️ **{row['title']}**  
        **Price:** {row['price']}  
        **Original Price:** {row['claimed_orig_price']}  
        **Discount:** {row['discount_percentage']}  
        **Store:** {row['store']}  
        **Category:** {row['category']}  
        **Freshness:** {row['freshness']}  
        🔗 [View Deal]({row['link'].split('](')[-1][:-1]})
        """)
        st.divider()

def to_readable_data(data):
    searched_df = pd.DataFrame(data)
    if not searched_df.empty:
        # Parse time_stamp
        searched_df["time_stamp"] = pd.to_datetime(searched_df["time_stamp"])

        # Add freshness info
        searched_df["days_old"] = (datetime.now() - searched_df["time_stamp"]).dt.days
        searched_df["freshness"] = searched_df["days_old"].apply(lambda d: "🟢 Fresh" if d <= 14 else "⚪ Stale")

        # Format price and discount
        searched_df["price"] = searched_df["price"].apply(lambda x: f"${x:,.2f}")
        searched_df["claimed_orig_price"] = searched_df["claimed_orig_price"].apply(lambda x: f"${x:,.2f}")
        searched_df["discount_percentage"] = searched_df["discount_percentage"].apply(lambda x: f"{x:.2f}%")

        # Shorten long titles
        searched_df["title"] = searched_df["title"].apply(lambda x: x if len(x) < 80 else x[:77] + "...")

        # Make URLs clickable
        searched_df["link"] = searched_df["url"].apply(lambda x: f"[🔗 View Deal]({x})")

        st.subheader("🖥️ Search Results")

        render_deals(searched_df)
    else:
        st.info("No results found . Try scraping it.")


def render():
    st.subheader("Find deals.")
    searcher = QuerySearcher()

    search_mode = st.radio("**Search by :**", ["By title", "By price"])

    if search_mode == "By title":
        keyword = st.text_input("Enter keyword:", "computer")
        searcher_btn = st.button("Search.")

        if searcher_btn:
            output = searcher.search_by_title(keyword, limit=10)

            to_readable_data(output)

    elif search_mode == "By price":

        st.subheader("***Search by title and price***")

        keyword = st.text_input("Enter keyword : ", "computer")
        price = st.number_input("enter price", 500)
        searcher_btn = st.button("search.")

        if searcher_btn and keyword and price:
            output = searcher.search_closest_price(keyword, price)

            # Convert to DataFrame
            to_readable_data(output)

