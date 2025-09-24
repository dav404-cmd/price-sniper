import pandas as pd
import streamlit as st

from scraper.scraper_runner_bs4 import run_by_categories, run_by_search
from ai_agents.suggestion_provider.suggester import SalesAssistantAgent,DummyLLM
from ai_agents.suggestion_provider.tools.querysearch_tools import QuerySearcher
import json
import os
from datetime import datetime, timedelta

from manage_db.db_manager import PostgresDB

st.set_page_config(layout="wide")


#CSV path that resets every run.(name is wrong.)
csv_path = "data/raw/cate_based_deals.csv"

#list of category.
category_data = "data/helper_data/slick_category.json"
with open(category_data,"r") as f:
    categories = json.load(f)


#-----Helping functions-----

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



st.header("Price Sniper")

tab1,tab2,tab4,tab3 = st.tabs(["Scrape Data","Explore Data","Find Data","Sales assistant."])

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
                df = pd.read_csv(csv_path)
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
                df = pd.read_csv(csv_path)
                st.session_state["scraped_table"] = df

            # Display cached table if available
        if "scraped_table" in st.session_state:
            st.subheader("Scraped Data.")
            st.dataframe(st.session_state["scraped_table"], use_container_width=True)




with tab2:

    #fixme: may need to switch to SQLAlchemy.

    if st.button("Show or Refresh Table", key="refresh_table"):
        db = PostgresDB()

        two_weeks_ago = datetime.now() - timedelta(days=14)

        # Query 1: Recent 79%+ discount deals based on time_stamp
        query = """
            SELECT * FROM listings
            WHERE discount_percentage > 79
            AND time_stamp >= %s
            ORDER BY time_stamp DESC
        """
        df = pd.read_sql(query, db.conn, params=[two_weeks_ago])

        st.subheader("🔥 Recent 79%+ Discount Deals")
        st.dataframe(df, use_container_width=True)

        st.divider()

        # Query 2: Other recent deals (not necessarily 79%+)
        fallback_query = """
            SELECT * FROM listings
            WHERE time_stamp >= %s
            ORDER BY time_stamp DESC
            LIMIT 100
        """
        fallback_df = pd.read_sql(fallback_query, db.conn, params=[two_weeks_ago])

        st.subheader("🧮 Other Recent Deals")
        st.dataframe(fallback_df, use_container_width=True)

        db.close()


with tab4:
    st.subheader("Find deals.")
    searcher = QuerySearcher()

    search_mode = st.radio("**Search by :**",["By title","By price"])

    if search_mode == "By title":
        keyword = st.text_input("Enter keyword:", "computer")
        searcher_btn = st.button("Search.")

        if searcher_btn:
            output = searcher.search_by_title(keyword, limit=10)

            # Convert to DataFrame
            keyword_df = pd.DataFrame(output)

            # Parse time_stamp
            keyword_df["time_stamp"] = pd.to_datetime(keyword_df["time_stamp"])

            # Add freshness info
            keyword_df["days_old"] = (datetime.now() - keyword_df["time_stamp"]).dt.days
            keyword_df["freshness"] = keyword_df["days_old"].apply(lambda d: "🟢 Fresh" if d <= 14 else "⚪ Stale")

            # Format price and discount
            keyword_df["price"] = keyword_df["price"].apply(lambda x: f"${x:,.2f}")
            keyword_df["claimed_orig_price"] = keyword_df["claimed_orig_price"].apply(lambda x: f"${x:,.2f}")
            keyword_df["discount_percentage"] = keyword_df["discount_percentage"].apply(lambda x: f"{x:.2f}%")

            # Shorten long titles
            keyword_df["title"] = keyword_df["title"].apply(lambda x: x if len(x) < 80 else x[:77] + "...")

            # Make URLs clickable
            keyword_df["link"] = keyword_df["url"].apply(lambda x: f"[🔗 View Deal]({x})")

            st.subheader("🖥️ Search Results")

            render_deals(keyword_df)

    elif search_mode == "By price":

        st.subheader("***Search by title and price***")

        keyword = st.text_input("Enter keyword : ","computer")
        price = st.number_input("enter price",500)
        searcher_btn = st.button("search.")

        if searcher_btn and keyword and price:
            output = searcher.search_closest_price(keyword, price)

            # Convert to DataFrame
            closest_price_df = pd.DataFrame(output)

            # Parse time_stamp
            closest_price_df["time_stamp"] = pd.to_datetime(closest_price_df["time_stamp"])

            # Add freshness info
            closest_price_df["days_old"] = (datetime.now() - closest_price_df["time_stamp"]).dt.days
            closest_price_df["freshness"] = closest_price_df["days_old"].apply(lambda d: "🟢 Fresh" if d <= 14 else "⚪ Stale")

            # Format price and discount
            closest_price_df["price"] = closest_price_df["price"].apply(lambda x: f"${x:,.2f}")
            closest_price_df["claimed_orig_price"] = closest_price_df["claimed_orig_price"].apply(lambda x: f"${x:,.2f}")
            closest_price_df["discount_percentage"] = closest_price_df["discount_percentage"].apply(lambda x: f"{x:.2f}%")

            # Shorten long titles
            closest_price_df["title"] = closest_price_df["title"].apply(lambda x: x if len(x) < 80 else x[:77] + "...")

            # Make URLs clickable
            closest_price_df["link"] = closest_price_df["url"].apply(lambda x: f"[🔗 View Deal]({x})")

            st.subheader("🖥️ Search Results")

            render_deals(closest_price_df)

    st.divider()


llm = DummyLLM()
agent = SalesAssistantAgent(llm)


with tab3:
    st.header("🛍️ AI Sales Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Create two containers: one for messages, one for input
    messages_container = st.container()
    input_container = st.container()

    # Chat input (always at bottom)
    with input_container:
        user_input = st.chat_input("Ask me about deals, products, or prices...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = agent.run(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Display messages (latest at bottom)
    with messages_container:
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).markdown(msg["content"])







