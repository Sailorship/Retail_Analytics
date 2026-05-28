import streamlit as st
import pandas as pd
from upload import upload


st.title("Retail Analytics Dashboard")

uploaded = st.file_uploader(
    "Upload Inventory File",
    type=["csv", "xlsx"]
)
submit = st.button("Submit")


if uploaded is not None and submit:

    if uploaded.name.endswith(".csv"):
        report = pd.read_csv(uploaded)

    else:
        report = pd.read_excel(uploaded)

    metrics, weekly_trend, missing_cols = upload(report)
    if metrics is None:
        st.error(f"Your file is missing required columns: {', '.join(missing_cols)}. Please check your export format.")
        st.stop()

    st.session_state['metrics'] = metrics
    st.session_state['report'] = report
    st.session_state['weekly_trend'] = weekly_trend


if 'metrics' in st.session_state:

    metrics = st.session_state['metrics']
    report = st.session_state['report']
    weekly_trend = st.session_state['weekly_trend']


    counts = metrics["Tracking"].value_counts()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fast-Moving", counts.get("Fast_Moving", 0))
    with col2:
        st.metric("Slow-Moving", counts.get("Slow_Moving", 0))
    with col3:
        st.metric("Deadstock", counts.get("Deadstock", 0))


    # Sidebar
    st.sidebar.metric("Total Revenue", f"₹{metrics['Revenue'].sum():,.0f}")
    st.sidebar.metric("Gross Profit", f"₹{metrics['Gross Profit'].sum():,.0f}")
    st.sidebar.metric("Profit Margin", f'{metrics['Profit Margin'].mean():.1f}%')


    thres = st.number_input(
        "Enter when you want to be alerted for low stock", value=7
    )

    # Analytics
    tab1, tab2, tab3 = st.tabs(['Low-stock','Deadstock', 'Analytics'])
    with tab1:
        # Low stock warning
        low_stock = metrics[metrics["Days_Remaining"] < thres]
        if low_stock.empty:
            st.success("No stocks needed.")
        else:
            st.warning(f'{len(low_stock)} items in the inventory need your attention.')

            with st.expander("Low stocks pending actions"):
                for category, group in low_stock.groupby("Category"):
                    with st.expander(f"{category}"):
                        for _, row in group.iterrows():
                            st.write(f"{row['Product Name']} - runs out in {row['Days_Remaining']:.0f} days")

    with tab2:
        # Deadstock warning
        deadstock = metrics[metrics["Tracking"] == "Deadstock"]

        if deadstock.empty:
            st.success("No deadstocks.")
        else:
            st.warning(f'{len(deadstock)} items in your inventory need actions!')

            with st.expander("Deadstock actions pending."):
                for category, group in deadstock.groupby("Category"):
                    with st.expander(f"{category}"):
                        for _, row in group.iterrows():
                            st.write(f"{row['Product Name']} is not moving. Consider a Discount or Promotion.")

    with tab3:
        # Category-by Profit
        st.subheader("Category-wise Gross Profit")
        category_profit = metrics.groupby("Category")["Gross Profit"].sum()
        st.bar_chart(category_profit)

        # Weekly Trends
        st.subheader('Weekly Trend')
        st.line_chart(weekly_trend.set_index('Date')['Units Sold'])


        #Top best 5 and top worst 5 products
        Top_best = metrics.sort_values(by="Gross Profit", ascending=False).head(5)
        Top_worst = metrics.sort_values(by="Gross Profit", ascending=True).head(5)

        Top_best["Gross Profit"] = Top_best["Gross Profit"].apply(lambda x: f"₹{x:,.0f}")
        Top_worst["Gross Profit"] = Top_worst["Gross Profit"].apply(lambda x: f"₹{x:,.0f}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 5 Best Performing Products!")
            st.dataframe(Top_best[["Product Name", "Gross Profit"]], hide_index=True)
        with col2:
            st.subheader("Bottom 5 Worst Performing Products!")
            st.dataframe(Top_worst[["Product Name", "Gross Profit"]], hide_index=True)


    # Data
    tab1, tab2 = st.tabs(["Retail Analytics", "Your Raw Inventory Data"])
    with tab1:
        # Data Read/Display
        st.subheader("Retail Analytics")
        st.dataframe(metrics[["Product Name", "Tracking", "Category", "Stock Status"]])
    with tab2:
        st.subheader("Raw Inventory Data")
        st.dataframe(report)

