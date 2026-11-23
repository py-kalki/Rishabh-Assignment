"""Builds and executes RetailMart_Sales_Analysis.ipynb."""
import nbformat as nbf
from nbclient import NotebookClient

from insights import INSIGHTS, RECOMMENDATIONS

INSIGHTS_MD = "## 7. Key Insights\n" + "\n".join(
    f"{i}. **{t}** – {b}" for i, (t, b) in enumerate(INSIGHTS, 1)
) + "\n\n## 8. Recommendations for the Owner\n" + "\n".join(
    f"{i}. **{t}** – {b}" for i, (t, b) in enumerate(RECOMMENDATIONS, 1)
) + "\n\n## 9. Conclusion\nRetailMart earned about **Rs 13.3 lakh** from 492 valid orders across 168 customers. " \
    "Most of that comes from Indore, from Electronics and Home & Kitchen, and from the Jun–Oct season. " \
    "The main risk is customer satisfaction: about a third of orders were rated 1 or 2. " \
    "Fixing that and spending the marketing budget where the sales already are should give the best returns."

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s))
code = lambda s: C.append(nbf.v4.new_code_cell(s))

md("""# RetailMart Sales Analysis – Python Mini Project
**BBA III Semester | Data Analysis using Python (BBADSE26303D) | IPS Academy, IBMR Indore**

**Objective:** Analyse one year of RetailMart sales data (Apr 2025 – Mar 2026) and give the owner clear, data-backed advice.

**Contents**
1. Import libraries & load data
2. Data cleaning
3. Net sales & key metrics
4. Group-wise analysis (city, category, month, top products)
5. Charts
6. Insights & recommendations""")

md("## 1. Import Libraries & Load Data")
code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110
os.makedirs("charts", exist_ok=True)

df = pd.read_csv("retailmart_sales database.csv")
print("Shape:", df.shape)
df.head()""")
code("df.info()")
code("df.describe()")

md("## 2. Data Cleaning\nFirst we check the problems in the raw data.")
code("""print("Duplicate rows        :", df.duplicated().sum())
print("Invalid quantity (<=0):", (df["quantity"] <= 0).sum())
print("Missing values:\\n", df.isnull().sum()[df.isnull().sum() > 0])
print("\\nCity spellings:\\n", df["city"].value_counts())""")

md("### 2.1 Remove duplicate rows")
code("""before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows -> {len(df)} rows left")""")

md("### 2.2 Remove invalid quantities\nA quantity of zero or less is impossible for a sale, so those rows are dropped.")
code("""before = len(df)
df = df[df["quantity"] > 0]
print(f"Removed {before - len(df)} rows with invalid quantity -> {len(df)} rows left")""")

md("### 2.3 Standardise city names\nNames like `indore`, `INDORE` and `Indore` are the same city, so we convert them all to Title Case.")
code("""df["city"] = df["city"].str.strip().str.title()
df["city"].value_counts()""")

md("### 2.4 Fill missing ratings and payment modes\n* **customer_rating** → filled with the **median** rating, which outliers don't pull up or down.\n* **payment_mode** → filled with the **mode** (the most common payment method).")
code("""median_rating = df["customer_rating"].median()
mode_payment = df["payment_mode"].mode()[0]
print("Median rating used :", median_rating)
print("Mode payment used  :", mode_payment)

df["customer_rating"] = df["customer_rating"].fillna(median_rating)
df["payment_mode"] = df["payment_mode"].fillna(mode_payment)
print("\\nMissing values now:", df.isnull().sum().sum())""")

md("### 2.5 Convert dates")
code("""df["order_date"] = pd.to_datetime(df["order_date"])
df["month"] = df["order_date"].dt.to_period("M")
df = df.reset_index(drop=True)
print(df.dtypes)
print("\\nDate range:", df["order_date"].min().date(), "to", df["order_date"].max().date())
print("Clean data shape:", df.shape)""")

md("## 3. Net Sales & Key Metrics\n**Net sales = quantity × unit price × (1 − discount%/100)**")
code("""df["net_sales"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)

total_sales = df["net_sales"].sum()
avg_order_value = df["net_sales"].mean()
unique_customers = df["customer_id"].nunique()
total_orders = df["order_id"].nunique()

print(f"Total Net Sales     : Rs {total_sales:,.0f}")
print(f"Total Orders        : {total_orders}")
print(f"Average Order Value : Rs {avg_order_value:,.0f}")
print(f"Unique Customers    : {unique_customers}")
print(f"Average Rating      : {df['customer_rating'].mean():.2f} / 5")
df[["order_id", "quantity", "unit_price", "discount_pct", "net_sales"]].head()""")

md("## 4. Group-wise Analysis\n### 4.1 Sales by City")
code("""city_sales = (df.groupby("city")
                .agg(net_sales=("net_sales", "sum"), orders=("order_id", "count"),
                     avg_rating=("customer_rating", "mean"))
                .sort_values("net_sales", ascending=False))
city_sales["share_%"] = (city_sales["net_sales"] / total_sales * 100).round(1)
city_sales.round(2)""")

md("### 4.2 Sales by Category")
code("""cat_sales = (df.groupby("category")
               .agg(net_sales=("net_sales", "sum"), orders=("order_id", "count"),
                    avg_discount=("discount_pct", "mean"), avg_rating=("customer_rating", "mean"))
               .sort_values("net_sales", ascending=False))
cat_sales["share_%"] = (cat_sales["net_sales"] / total_sales * 100).round(1)
cat_sales.round(2)""")

md("### 4.3 Sales by Month")
code("""month_sales = df.groupby("month").agg(net_sales=("net_sales", "sum"), orders=("order_id", "count"))
month_sales""")

md("### 4.4 Top 5 Products (by net sales)")
code("""top5 = (df.groupby(["product", "category"])
          .agg(net_sales=("net_sales", "sum"), units=("quantity", "sum"))
          .sort_values("net_sales", ascending=False).head(5))
top5""")

md("### 4.5 Extra: Payment modes, ratings and discounts")
code("""print("Payment mode share (% of orders):")
print((df["payment_mode"].value_counts(normalize=True) * 100).round(1))
print("\\nRating distribution:")
print(df["customer_rating"].value_counts().sort_index())
print("\\nAverage order value by discount level:")
print(df.groupby("discount_pct")["net_sales"].agg(["count", "mean"]).round(0))""")

md("## 5. Charts")
md("### Chart 1 – Sales by City")
code("""fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(city_sales.index, city_sales["net_sales"] / 1000, color="#2E86AB")
ax.bar_label(bars, labels=[f"{v/1000:.0f}K" for v in city_sales["net_sales"]], padding=3)
ax.set_title("Net Sales by City", fontsize=14, fontweight="bold")
ax.set_xlabel("City"); ax.set_ylabel("Net Sales (Rs '000)")
plt.tight_layout(); plt.savefig("charts/1_city_sales.png"); plt.show()""")

md("### Chart 2 – Category Share")
code("""fig, ax = plt.subplots(figsize=(6.5, 6.5))
ax.pie(cat_sales["net_sales"], labels=cat_sales.index, autopct="%1.1f%%", startangle=90,
       colors=sns.color_palette("Set2"), wedgeprops=dict(edgecolor="white"))
ax.set_title("Share of Net Sales by Category", fontsize=14, fontweight="bold")
plt.tight_layout(); plt.savefig("charts/2_category_share.png"); plt.show()""")

md("### Chart 3 – Monthly Sales Trend")
code("""fig, ax = plt.subplots(figsize=(10, 4.5))
labels = month_sales.index.strftime("%b-%y")
ax.plot(labels, month_sales["net_sales"] / 1000, marker="o", linewidth=2.5, color="#E07A5F")
ax.axhline(month_sales["net_sales"].mean() / 1000, ls="--", color="grey", label="Monthly average")
ax.set_title("Monthly Net Sales Trend (Apr 2025 – Mar 2026)", fontsize=14, fontweight="bold")
ax.set_xlabel("Month"); ax.set_ylabel("Net Sales (Rs '000)"); ax.legend()
plt.tight_layout(); plt.savefig("charts/3_monthly_trend.png"); plt.show()""")

md("### Chart 4 – Customer Ratings")
code("""fig, ax = plt.subplots(figsize=(7, 4.5))
rc = df["customer_rating"].value_counts().sort_index()
bars = ax.bar(rc.index.astype(int).astype(str), rc.values, color=sns.color_palette("RdYlGn", 5))
ax.bar_label(bars, padding=3)
ax.set_title("Distribution of Customer Ratings", fontsize=14, fontweight="bold")
ax.set_xlabel("Rating (1 = worst, 5 = best)"); ax.set_ylabel("Number of Orders")
plt.tight_layout(); plt.savefig("charts/4_ratings.png"); plt.show()""")

md("### Chart 5 – City × Category Heatmap")
code("""pivot = df.pivot_table(index="city", columns="category", values="net_sales", aggfunc="sum").fillna(0)
pivot = pivot.loc[city_sales.index, cat_sales.index]
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(pivot / 1000, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5,
            cbar_kws={"label": "Net Sales (Rs '000)"}, ax=ax)
ax.set_title("Net Sales Heatmap: City × Category (Rs '000)", fontsize=14, fontweight="bold")
ax.set_xlabel("Category"); ax.set_ylabel("City")
plt.tight_layout(); plt.savefig("charts/5_heatmap.png"); plt.show()""")

md("### Chart 6 (extra) – Top 5 Products & Payment Modes")
code("""fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
t = top5.reset_index().sort_values("net_sales")
axes[0].barh(t["product"], t["net_sales"] / 1000, color="#81B29A")
axes[0].set_title("Top 5 Products by Net Sales", fontweight="bold")
axes[0].set_xlabel("Net Sales (Rs '000)"); axes[0].set_ylabel("Product")
pm = df["payment_mode"].value_counts()
axes[1].bar(pm.index, pm.values, color="#3D405B")
axes[1].set_title("Orders by Payment Mode", fontweight="bold")
axes[1].set_xlabel("Payment Mode"); axes[1].set_ylabel("Number of Orders")
plt.tight_layout(); plt.savefig("charts/6_products_payment.png"); plt.show()""")

md("## 6. Summary numbers used in the insights")
code("""best_m, worst_m = month_sales["net_sales"].idxmax(), month_sales["net_sales"].idxmin()
low = (df["customer_rating"] <= 2).mean() * 100
print(f"Top city        : {city_sales.index[0]} ({city_sales['share_%'].iloc[0]}% of sales)")
print(f"Top 2 cities    : {city_sales['share_%'].iloc[:2].sum():.1f}% of sales")
print(f"Top category    : {cat_sales.index[0]} ({cat_sales['share_%'].iloc[0]}%)")
print(f"Best month      : {best_m} (Rs {month_sales['net_sales'].max():,.0f})")
print(f"Weakest month   : {worst_m} (Rs {month_sales['net_sales'].min():,.0f})")
print(f"UPI share       : {(df['payment_mode']=='UPI').mean()*100:.1f}% of orders")
print(f"Low ratings (<=2): {low:.1f}% of orders")
print(f"Orders/customer : {total_orders/unique_customers:.2f}")""")

md(INSIGHTS_MD)

nb["cells"] = C
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": "."}}).execute()
nbf.write(nb, "RetailMart_Sales_Analysis.ipynb")
print("done")
