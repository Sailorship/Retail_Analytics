import pandas as pd
import numpy as np


def upload(report):
    report.columns = report.columns.str.strip()
    report['Date'] = pd.to_datetime(report['Date'])
    days = (report['Date'].max() - report['Date'].min()).days
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
    metrics["Inventory_TR"] = (COGS / ((report["Opening Stock"] + report['Closing Stock']) / 2))
    metrics["Days_Remaining"] = (report["Closing Stock"] / metrics["Sales_Velocity"]).round(0)
    metrics['Revenue'] = (report['Units Sold'] * report['Sale Price'])
    metrics['Cost'] = (report['Units Sold'] * report['Purchase Price'])
    metrics['Gross Profit'] = (metrics['Revenue'] - metrics['Cost'])
    metrics['Profit Margin'] = ((metrics['Gross Profit'] / metrics['Revenue']) * 100)
    metrics["Days_Remaining"] = metrics["Days_Remaining"].clip(lower=0)
    metrics["Stock Status"] = metrics["Days_Remaining"].apply(
        lambda x: "Out of Stock" if x == 0 else ("No Sales" if x == float('inf') else f"{int(x)} {'day' if x == 1 else 'days'}")
    )


    cond = [
        metrics["Days_Remaining"] <= 15,
        (metrics["Days_Remaining"] > 15) & (metrics["Days_Remaining"] <= 60),
        metrics["Days_Remaining"] > 60
    ]

    choices = [
        'Fast_Moving',
        'Slow_Moving',
        'Deadstock'
    ]

    metrics["Tracking"] = np.select(cond, choices, default="Unknown")

    return metrics, weekly_trend



