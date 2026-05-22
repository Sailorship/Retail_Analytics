import pandas as pd
import numpy as np


def upload(report):
    metrics = report[["SKU", "Product_Name", "Category"]].copy()

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    metrics["Sales_Velocity"] = (report["Units_Sold"] / report["Days"])
    metrics["Inventory_TR"] = (report["COGS"] / report["Avg_Inventory"])
    metrics["Days_Remaining"] = (report["Current_Stock"] / metrics["Sales_Velocity"])


    cond = [
        metrics["Inventory_TR"] >= 3,
        (metrics["Inventory_TR"] >= 1) & (metrics["Inventory_TR"] < 3),
        metrics["Inventory_TR"] < 1
    ]

    choices = [
        'Fast_Moving',
        'Slow_Moving',
        'Deadstock'
    ]

    metrics["Tracking"] = np.select(cond, choices, default="Unknown")

    return metrics



