import pandas as pd
import streamlit as st
from manage_db.db_manager import PostgresDB
import plotly.express as px


def render():
    st.subheader("Data Visualization.")
    mode = st.radio("**Visualize :**", ["price v discount", "store v discount"])

    if mode == "price v discount":

        _db = PostgresDB()
        engine = _db.get_db_engine()

        query = "SELECT * FROM listings"


        df = pd.read_sql(query, engine)

        min_disc, max_disc = st.slider("Filter by discount %", 0, 100, (50, 100))
        col1,col2 = st.columns(2)

        with col1:
            store_options = df['store'].value_counts().nlargest(10).index.tolist()
            selected_store = st.selectbox("Select a store to explore:", store_options)

            filtered_df = df.loc[
                (df['store'] == selected_store) &
                (df['discount_percentage'].between(min_disc, max_disc))
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

        with col2:
            top_stores = df['store'].value_counts().nlargest(10).index
            filtered_df_2 = df[df['store'].isin(top_stores)]
            filtered_df_2 = filtered_df_2[
                (filtered_df_2["discount_percentage"] >= min_disc) &
                (filtered_df_2["discount_percentage"] <= max_disc)
                ]

            fig2 = px.scatter(
                filtered_df_2,
                x = "price",
                y = "discount_percentage",
                color = "store",
                hover_data=["title", "claimed_orig_price", "discount_percentage", "url"],
                title="Price vs Discount of top 10 store"
            )
            fig2.update_layout(yaxis_range = [0,100])

            st.markdown("<br><br><br>", unsafe_allow_html=True) #Spaces

            st.plotly_chart(fig2,use_container_width=True)

        st.subheader(f"*Deals of {selected_store} of discount ({min_disc} - {max_disc})*")
        st.dataframe(filtered_df[["title", "price", "discount_percentage", "url"]])



    elif mode == "store v discount":

        vis_tab1,vis_tab2 = st.tabs(["Top stores by discount","Top stores by deals listing"])

        _db = PostgresDB()
        engine = _db.get_db_engine()

        query = "SELECT * FROM listings"
        df = pd.read_sql(query, engine)

        with vis_tab1:
            top_n = st.slider("Show top N stores", 5, 30, 10,key = "slider_1")
            avg_disc = (
                df.groupby("store")["discount_percentage"].mean().sort_values(ascending=False).head(top_n).reset_index()
            )
            fig = px.bar(
                avg_disc,
                x="store",
                y="discount_percentage",
                text="discount_percentage",
                title=f"Top {top_n} Stores by Average Discount %",
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

            fig.update_layout(yaxis_range=[0, 100])

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Average Discount % per Store")
            st.dataframe(avg_disc)


        with vis_tab2:
            st.divider()
            top_n = st.slider("Show top N stores", 5, 30, 10,key = "slider_2")
            top_stores = (
                df['store'].value_counts().head(top_n).index
            )
            filtered_df = df[df['store'].isin(top_stores)]

            avg_disc = (
                filtered_df.groupby("store")["discount_percentage"].mean().sort_values(ascending=False).reset_index()
            )

            fig = px.bar(
                avg_disc,
                x="store",
                y="discount_percentage",
                text="discount_percentage",
                title=f"Average Discount % of Top {top_n} Stores by Deal Count",
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Average Discount % per Store")
            st.dataframe(avg_disc)



