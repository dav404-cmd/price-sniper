import streamlit as st
from datetime import timedelta,datetime
import pandas as pd

from manage_db.db_manager import PostgresDB



def render():
    # fixme: may need to switch to SQLAlchemy.

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