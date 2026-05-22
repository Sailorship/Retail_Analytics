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

    metrics = upload(report)
    st.session_state['metrics'] = metrics
    st.session_state['report'] = report


if 'metrics' in st.session_state:

    metrics = st.session_state['metrics']
    report = st.session_state['report']

    counts = metrics["Tracking"].value_counts()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fast-Moving", counts["Fast_Moving"])
    with col2:
        st.metric("Slow-Moving", counts["Slow_Moving"])
    with col3:
        st.metric("Deadstock", counts["Deadstock"])


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
                        st.write(f"{row['Product_Name']} - runs out in {row['Days_Remaining']:.0f} days")

        #Deadstock warning
        deadstock = metrics[metrics["Tracking"] == "Deadstock"]

        if deadstock.empty:
            st.success("No deadstocks.")
        else:
            st.warning(f'{len(deadstock)} items in your nventory need actions!')

        with st.expander("Deadstock actions pending."):
            for category, group in deadstock.groupby("Category"):
                with st.expander(f"{category}"):
                    for _, row in group.iterrows():
                        st.write(f"{row['Product_Name']} is not moving. Consider a Discount or Promotion.")


    st.subheader("Retail Analytics")
    st.dataframe(metrics[["Product_Name", "Tracking", "Category", "Days_Remaining"]])
    st.subheader("Raw Inventory Data")
    st.dataframe(report)

