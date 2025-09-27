import pandas as pd
import streamlit as st
import seaborn as sns
from manage_db.db_manager import PostgresDB
import plotly.express as px


def render():
    st.subheader("Data Visualization.")
    mode = st.radio("**Visualize :**", ["price v discount", "store v discount"])
    if mode == "price v discount":

        _db = PostgresDB()
        engine = _db.get_db_engine()
        query = "SELECT * FROM listings"

        sns.set(style="whitegrid")

        df = pd.read_sql(query, engine)

        store_options = df['store'].value_counts().nlargest(10).index.tolist()
        selected_store = st.selectbox("Select a store to explore:", store_options)

        filtered_df = df[df['store'] == selected_store]

        min_disc, max_disc = st.slider("Filter by discount %", 0, 100, (50, 100))
        filtered_df = filtered_df[
            (filtered_df["discount_percentage"] >= min_disc) &
            (filtered_df["discount_percentage"] <= max_disc)
            ]

        fig = px.scatter(
            filtered_df,
            x="price",
            y="discount_percentage",
            color="store",
            hover_data=["title", "claimed_orig_price", "discount_percentage", "url"],
            title=f"Price vs Discount for {selected_store}",
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(filtered_df[["title", "price", "discount_percentage", "url"]])

    elif mode == "store v discount":
        st.info("**under development**")
