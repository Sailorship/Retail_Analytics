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

    metrics, weekly_trend = upload(report)
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

    # Category-by Profit
    st.subheader("Category-wise Gross Profit")
    category_profit = metrics.groupby("Category")["Gross Profit"].sum()
    st.bar_chart(category_profit)

    st.subheader('Weekly Trend')
    st.line_chart(weekly_trend.set_index('Date')['Units Sold'])

    # Sidebar
    st.sidebar.metric("Total Revenue", f"₹{metrics['Revenue'].sum():,.0f}")
    st.sidebar.metric("Gross Profit", f"₹{metrics['Gross Profit'].sum():,.0f}")
    st.sidebar.metric("Profit Margin", f'{metrics['Profit Margin'].mean():.1f}%')


    thres = st.number_input(
        "Enter when you want to be alerted for low stock", value=7
    )
    #Low stock warning
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

        #Deadstock warning
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



    st.subheader("Retail Analytics")
    st.dataframe(metrics[["Product Name", "Tracking", "Category", "Days_Remaining"]])
    st.subheader("Raw Inventory Data")
    st.dataframe(report)

