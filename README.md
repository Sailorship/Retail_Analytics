# Retail Inventory Analytics Dashboard

A decision-support dashboard for small retail store owners to manage inventory without technical knowledge.

Built with Python and Streamlit.

---

## What it does

Small store owners often have inventory data but no easy way to act on it. This tool takes their existing inventory export and surfaces clear, plain-language insights so they can make stock decisions without needing any technical background.

- **Automatic product classification** — identifies Fast-Moving, Slow-Moving, and Deadstock products using Sales Velocity and Inventory Turnover Ratio. Give bar and line graphs for the user visualize their report.  
- **Low stock alerts** — owner sets their own threshold (e.g. alert me when stock runs out within 7 days), and the tool shows exactly which products need attention, grouped by category
- **Deadstock recommendations** — flags products not moving and suggests action (discount or promotion)
- **KPI summary cards** — instant overview of how many products fall into each category
- **Plain language throughout** — no jargon, designed for non-technical users

---

## How to run

**1. Clone the repository**
```
git clone https://github.com/Sailorship/Retail_Analytics.git
cd Retail_Analytics
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Run the app**
```
streamlit run app.py
```

**4. Upload your inventory file**

The tool accepts CSV or Excel files with the following columns:

| Column         | Description               |
|----------------|---------------------------|
| Date           | Date of the inventory record                          |
| Product Name   | Name of the product       |
| Category       | Store category (e.g. Grocery, Snacks) |
| Tracking       | Store category (e.g. Grocery, Snacks) |
| Units Sold     | Number of units sold in the period |
| Opening Stock  | Units of stock available at the start of the period. |
| Closing Stock  | Units of stock remaining at the end of the period. Used to calculate days remaining.   |
| Purchase Price |  Cost per unit paid to the supplier. Used to calculate COGS and gross profit        |
| Sale Price     | Price per unit charged to customers. Used to calculate revenue and profit margin.        |

A sample inventory file is included in the repository for testing.

Supports multiple store types - tested with departmental stores and clothing stores

---

## Tech stack

- Python
- Pandas
- NumPy
- Streamlit

---

## Background

This project was built from firsthand retail operations experience. The analytics logic — Sales Velocity, Inventory Turnover Ratio, Days Remaining, and product classification — was designed to surface insights that store owners already have access to in their systems but rarely act on, because existing tools don't present them in a usable way.

---

## Status

Working prototype. Built as a portfolio project while pursuing MCA at Kristu Jayanti College, Bangalore.
