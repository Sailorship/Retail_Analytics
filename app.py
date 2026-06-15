import streamlit as st
import pandas as pd


from upload import upload


st.title("Retail Analytics Dashboard")

uploaded = st.file_uploader(
    "Upload Inventory File",
    type=["csv", "xlsx"]
)
submit = st.button("Submit")
lead_time = st.number_input("How many days does your supplier take to deliver?", value=2, min_value=1)

if uploaded is not None and submit:

    if uploaded.name.endswith(".csv"):
        report = pd.read_csv(uploaded)

    else:
        report = pd.read_excel(uploaded)

    metrics, weekly_trend, missing_cols = upload(report, lead_time)
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

    thres = st.number_input(
        'Alert me when the stock is less than ___ days away.', value=7
    )


    counts = metrics["Tracking"].value_counts()
    fast_moving = metrics[metrics["Tracking"] == "Fast Moving"]
    deadstock = metrics[metrics["Tracking"] == "Deadstock"]
    slow_moving = metrics[metrics["Tracking"] == "Slow Moving"]
    low_stock = metrics[metrics["Closing Stock"] <= metrics["Reorder_Point"]]
    category_profit = metrics.groupby("Category")["Gross Profit"].sum()
    reorder_qty = (metrics["Sales_Velocity"] * thres) + metrics["Safety_Stock"]

    # AI Summary for the app
    st.info(f"""
    >Summary:\n
    Your store has {counts.get('Fast Moving', 0)} fast-moving products, 
    {counts.get('Slow Moving', 0)} slow-moving, and {counts.get('Deadstock', 0)} deadstock items.
    {len(low_stock)} products need restocking within {thres} days.
    Your most profitable category is {category_profit.idxmax()}.
    Total revenue this period: ₹{metrics['Revenue'].sum():,.0f} with a profit margin of {metrics['Profit Margin'].mean():.1f}%.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fast-Moving", counts.get("Fast Moving", 0))
        with st.expander("View Products"):
            for _, row in fast_moving.iterrows():
                st.write(f"{row['Product Name']}")
            st.write(">>These are your best selling products based on your sales per day.")
    with col2:
        st.metric("Slow-Moving", counts.get("Slow Moving", 0))
        with st.expander("View Products"):
            for _, row in slow_moving.iterrows():
                st.write(f"{row['Product Name']} ")
            st.write(">>These products are selling slower than your store average")
    with col3:
        st.metric("Deadstock", counts.get("Deadstock", 0))
        with st.expander("View Products"):
            if deadstock.empty:
                st.write(">>No Deadstock at the moment.")
            else:
                for _, row in deadstock.iterrows():
                    st.write(f"{row['Product Name']}")
                st.write(">>These products have the lowest sales in your store. Consider a discount or promotion.")



    # Sidebar
    st.sidebar.metric("Total Revenue", f"₹{metrics['Revenue'].sum():,.0f}")
    st.sidebar.metric("Gross Profit", f"₹{metrics['Gross Profit'].sum():,.0f}")
    st.sidebar.metric("Profit Margin", f'{metrics['Profit Margin'].mean():.1f}%')


    # Analytics

    tab1, tab2, tab3 = st.tabs(['Low-stock','Deadstock', 'Analytics'])
    with tab1:
        if low_stock.empty:
            st.success("All stock levels are healthy. No restocking needed.")
        else:
            st.warning(f"{len(low_stock)} items in the inventory need restock action.")
            with st.expander("Low stocks pending actions"):
                for category, group in low_stock.groupby("Category"):
                    st.markdown(f"**{category}**")
                    for _, row in group.iterrows():
                        name = row["Product Name"]
                        stock = int(row["Closing Stock"])
                        days = row["Days_Remaining"]
                        qty = int(row["Reorder_Qty"])
                        tracking = row["Tracking"]
                        status = row["Stock Status"]

                        if status == "Out of Stock":
                            if tracking == "Fast Moving":
                                st.error(
                                    f"**{name}** — Out of Stock.\n\n"
                                    f"Fast seller — restock immediately.\n\n"
                                    f"Order **{qty} units** to cover the next 30 days."
                                )
                            else:
                                st.warning(
                                    f"**{name}** — Out of Stock.\n\n"
                                    f"Consider restocking — order **{qty} units** to cover the next 30 days."
                                )

                        elif status == "Order Now":
                            days_text = f"Runs out in {int(days)} days" if days > 0 else "Very low stock"
                            st.error(
                                f"**{name}** — Order Now.\n\n"
                                f"Stock: {stock} units | {days_text}\n\n"
                                f"Order **{qty} units** to cover the next 30 days."
                            )
                        else:
                            days_text = f"Runs out in {int(days)} days" if days > 0 else "Out of Stock"
                            st.warning(
                                f"**{name}** — Order Soon.\n\n"
                                f"Stock: {stock} units | {days_text}\n\n"
                                f"Order **{qty} units** to cover the next 30 days."
                            )


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




