import pandas as pd
import numpy as np

column_mapping = {
    # Vyapar columns
    "Item Name": "Product Name",
    "Particulars": "Product Name",
    "Item Code": "SKU",
    "Inward / Purchase Qty": "Purchase Quantity",
    "Outward / Sale Qty": "Units Sold",
    "Purchase Qty": "Purchase Quantity",
    "Sale Qty": "Units Sold",
    "Closing Qty": "Closing Stock",
    "Opening Qty": "Opening Stock",

    # myBillBook columns
    "Outward / Sales Qty": "Units Sold",

    # Common variations
    "Item": "Product Name",
    "Product": "Product Name",
    "Stock Item": "Product Name",
    "Product_Name": "Product Name",
}

required_columns = ["Product Name", "Category", "Units Sold", "Opening Stock", "Closing Stock", "Purchase Price",
                    "Sale Price", "Date"]


def upload(report):
    report.columns = report.columns.str.strip()
    report = report.rename(columns=column_mapping)

    missing = [col for col in required_columns if col not in report.columns]
    if missing:
        return None, None, missing

    report['Date'] = pd.to_datetime(report['Date'])
    days = max((report['Date'].max() - report['Date'].min()).days, 1)
    report = report.sort_values(by='Date', ascending=True)

    weekly_trend = report.groupby('Date')['Units Sold'].sum().reset_index()
    weekly_trend = weekly_trend.sort_values('Date')

    # Group by Product Name
    report = report.groupby("Product Name").agg({
        "Category": "first",
        "Units Sold": "sum",
        "Opening Stock": "first",
        "Closing Stock": "last",
        "Purchase Quantity": "sum",
        "Purchase Price": "mean",
        "Sale Price": "mean"
    }).reset_index()

    COGS = report['Units Sold'] * report['Purchase Price']
    metrics = report[["Product Name", "Category"]].copy()

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    metrics["Sales_Velocity"] = (report["Units Sold"] / days)

    avg_inv = (report['Opening Stock'] + report['Closing Stock']) / 2
    metrics["Inventory_TR"] = COGS / avg_inv.replace(0, np.nan)

    metrics["Days_Remaining"] = (report["Closing Stock"] / metrics["Sales_Velocity"]).round(0)
    metrics['Revenue'] = (report['Units Sold'] * report['Sale Price'])
    metrics['Cost'] = (report['Units Sold'] * report['Purchase Price'])
    metrics['Gross Profit'] = (metrics['Revenue'] - metrics['Cost'])
    metrics['Profit Margin'] = metrics.apply(
        lambda row: 0 if row['Revenue'] == 0 else (row['Gross Profit'] / row['Revenue']) * 100, axis=1
    )
    metrics["Days_Remaining"] = metrics["Days_Remaining"].clip(lower=0)
    metrics["Stock Status"] = metrics["Days_Remaining"].apply(
        lambda x: "Out of Stock" if x == 0 else (
            "No Sales" if x == float('inf') else f"{int(x)} {'day' if x == 1 else 'days'}")
    )

    metrics["Tracking"] = pd.qcut(
        metrics["Sales_Velocity"],
        q=3,
        labels=["Deadstock", "Slow Moving", "Fast Moving"]
    )
    return metrics, weekly_trend, missing



