import pandas
import pandas as pd
import streamlit as st
from scraper.scraper_runner_bs4 import run_by_categories, run_by_search
from ai_agents.suggestion_provider.suggester import SalesAssistantAgent,DummyLLM
import json
import os

from manage_db.db_manager import PostgresDB

st.set_page_config(layout="wide")


#CSV path that resets every run.(name is wrong.)
csv_path = "data/raw/cate_based_deals.csv"

#list of category.
category_data = "data/helper_data/slick_category.json"
with open(category_data,"r") as f:
    categories = json.load(f)

st.header("Price Sniper")

tab1,tab2,tab4 = st.tabs(["Scrape Data","Explore Data","Sales assistant."])

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
        db = PostgresDB()

        df = pd.read_sql("SELECT * FROM listings", db.conn)
        db.close()

        tables = df[df["discount_percentage"] > 50]
        st.subheader("Great deals (50%+ discount)")
        st.dataframe(tables, use_container_width=True)

        st.divider()

        st.subheader("Some other deals")
        all_table = df.head(100)
        st.dataframe(all_table, use_container_width=True)




llm = DummyLLM()
agent = SalesAssistantAgent(llm)

with tab4:
    st.header("🛍️ AI Sales Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display previous messages
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask me about deals, products, or prices...")

    if user_input:
        # Show user message
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get assistant response
        response = agent.run(user_input)

        # Show assistant message
        st.chat_message("assistant").markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})



