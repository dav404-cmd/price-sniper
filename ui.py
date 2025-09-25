import streamlit as st

#tabs
from ui_tabs import scrape_tab,explore_tab,searcher_tab,agent_tab

st.set_page_config(layout="wide")

st.header("Price Sniper")

tab1,tab2,tab4,tab3 = st.tabs(["Scrape Data","Explore Data","Find Data","Sales assistant."])

with tab1:

    scrape_tab.render()

with tab2:

    explore_tab.render()

with tab4:

    searcher_tab.render()

with tab3:

    agent_tab.render()







