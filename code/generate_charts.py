"""
Generates all charts for the Retail Sales Data Visualization project.
Author: Abhay Kumar Verma | Roll No: 2026M01410112

Run:  python generate_charts.py
Output: PNG files in ./charts and key numbers in charts/stats.json
        (the stats are used to write the insight captions).
"""
import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from clean_data import load_and_clean

OUT = "charts"
os.makedirs(OUT, exist_ok=True)

# ---- consistent palette: one base colour, one highlight colour, one neutral ----
BLUE = "#2a78d6"      # default data colour
ORANGE = "#eb6834"    # highlight: the point being made
GREY = "#8a8985"      # neutral / reference lines
INK = "#1f1f1f"
SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#eaf2fc", "#2a78d6", "#0e2f5c"])
DIV = LinearSegmentedColormap.from_list("div", [ORANGE, "#f2f2f0", BLUE])
SEGMENT_COLORS = [BLUE, ORANGE, "#1baf7a"]

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.labelsize": 10, "axes.edgecolor": "#bbbbb8", "axes.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#ececea", "grid.linewidth": 0.6,
    "axes.axisbelow": True, "xtick.color": INK, "ytick.color": INK,
})

df = load_and_clean()
stats = {}


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", facecolor="white")
    plt.close(fig)


def inr_m(x, _=None):
    return f"₹{x/1e6:,.1f}M"


# 1. LINE: monthly sales trend ------------------------------------------------
m = df.groupby("Month")["Sales"].sum()
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(m.index, m.values, color=BLUE, lw=2, marker="o", ms=5, label="Monthly sales")
ax.plot(m.idxmax(), m.max(), "o", color=ORANGE, ms=9, mec="white", mew=2, label="Peak month")
ax.plot(m.idxmin(), m.min(), "o", color=GREY, ms=9, mec="white", mew=2, label="Lowest month")
ax.annotate(f"{m.idxmax():%b %Y}\n{inr_m(m.max())}", (m.idxmax(), m.max()),
            xytext=(0, 12), textcoords="offset points", ha="center", fontsize=9, color=INK)
ax.annotate(f"{m.idxmin():%b %Y}\n{inr_m(m.min())}", (m.idxmin(), m.min()),
            xytext=(0, -30), textcoords="offset points", ha="center", fontsize=9, color=INK)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(inr_m))
ax.set_ylim(0, m.max() * 1.18)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("Monthly sales, Jan 2023 – Dec 2024")
ax.set_xlabel("Order month"); ax.set_ylabel("Total sales (₹ millions)")
ax.legend(frameon=False, loc="lower right")
save(fig, "01_line_monthly_sales")
y = df.groupby("Year")["Sales"].sum()
h1 = m[:12].mean(); h2 = m[12:].mean()
stats["line"] = dict(peak=str(m.idxmax().date()), peak_val=m.max(), low=str(m.idxmin().date()),
                     low_val=m.min(), y2023=y[2023], y2024=y[2024],
                     growth=(y[2024] / y[2023] - 1) * 100, avg_month=m.mean(), cv=m.std() / m.mean() * 100)
# month-of-year seasonality
moy = df.groupby(df.Order_Date.dt.month)["Sales"].sum()
stats["line"]["best_moy"] = int(moy.idxmax()); stats["line"]["worst_moy"] = int(moy.idxmin())

# 2. BAR: sales by region -----------------------------------------------------
r = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 4))
cols = [ORANGE if k == r.idxmin() else BLUE for k in r.index]
bars = ax.bar(r.index, r.values, color=cols, width=0.6)
ax.bar_label(bars, labels=[inr_m(v) for v in r.values], padding=3, fontsize=9)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(inr_m)); ax.set_ylim(0, r.max() * 1.12)
ax.grid(axis="x", visible=False)
ax.set_title("Total sales by region"); ax.set_xlabel("Region"); ax.set_ylabel("Total sales (₹ millions)")
save(fig, "02_bar_sales_by_region")
stats["region"] = dict(r.round(0).to_dict(), top=r.idxmax(), bottom=r.idxmin(),
                       gap_pct=(r.max() / r.min() - 1) * 100, total=r.sum())

# 3. BAR: sales by category ---------------------------------------------------
c = df.groupby("Product_Category")["Sales"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7.5, 4))
cols = [ORANGE if k == c.idxmax() else BLUE for k in c.index]
bars = ax.barh(c.index[::-1], c.values[::-1], color=cols[::-1], height=0.6)
ax.bar_label(bars, labels=[f"{inr_m(v)} ({v/c.sum():.0%})" for v in c.values[::-1]], padding=3, fontsize=9)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(inr_m)); ax.set_xlim(0, c.max() * 1.25)
ax.grid(axis="y", visible=False)
ax.set_title("Total sales by product category"); ax.set_xlabel("Total sales (₹ millions)"); ax.set_ylabel("Product category")
save(fig, "03_bar_sales_by_category")
stats["category"] = dict(c.round(0).to_dict(), top=c.idxmax(), bottom=c.idxmin(),
                         top_share=c.max() / c.sum() * 100, bottom_share=c.min() / c.sum() * 100)

# 4. HISTOGRAM: age -----------------------------------------------------------
age = df["Age"].dropna()
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.hist(age, bins=25, color=BLUE, edgecolor="white", linewidth=0.8)
ax.axvline(age.mean(), color=ORANGE, lw=2, label=f"Mean = {age.mean():.1f}")
ax.axvline(age.median(), color=GREY, lw=2, ls="--", label=f"Median = {age.median():.0f}")
ax.set_title("Distribution of customer age"); ax.set_xlabel("Age (years)"); ax.set_ylabel("Number of transactions")
ax.legend(frameon=False)
save(fig, "04_hist_age")
stats["age"] = dict(mean=age.mean(), median=age.median(), skew=age.skew(), min=age.min(), max=age.max(),
                    share_25_45=((age >= 25) & (age <= 45)).mean() * 100)

# 5. HISTOGRAM: income (capped at 99th percentile) ------------------------------
inc = df["Income_Capped"].dropna()
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.hist(inc, bins=40, color=BLUE, edgecolor="white", linewidth=0.6)
ax.axvline(inc.mean(), color=ORANGE, lw=2, label=f"Mean = ₹{inc.mean():,.0f}")
ax.axvline(inc.median(), color=GREY, lw=2, ls="--", label=f"Median = ₹{inc.median():,.0f}")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1000:,.0f}K"))
ax.set_title("Distribution of customer income (capped at 99th percentile)")
ax.set_xlabel("Annual income (₹ thousands)"); ax.set_ylabel("Number of transactions")
ax.legend(frameon=False)
save(fig, "05_hist_income")
raw_inc = df["Income"].dropna()
stats["income"] = dict(mean=inc.mean(), median=inc.median(), skew_capped=inc.skew(), skew_raw=raw_inc.skew(),
                       raw_max=raw_inc.max(), cap=df["Income"].quantile(.99))

# 6. BOX: sales by category ---------------------------------------------------
order = df.groupby("Product_Category")["Sales"].median().sort_values(ascending=False).index
fig, ax = plt.subplots(figsize=(8.5, 4.5))
sns.boxplot(data=df, x="Product_Category", y="Sales", order=order, color=BLUE, width=0.55,
            fliersize=2.5, linewidth=1, flierprops=dict(markerfacecolor=GREY, markeredgecolor=GREY, alpha=.5),
            medianprops=dict(color=ORANGE, lw=2.2), ax=ax)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
ax.set_title("Sales per transaction by product category (log scale)")
ax.set_xlabel("Product category (ordered by median sales)"); ax.set_ylabel("Sales per transaction (₹, log scale)")
ax.grid(axis="x", visible=False)
save(fig, "06_box_sales_by_category")
g = df.groupby("Product_Category")["Sales"]
q1, q3 = g.quantile(.25), g.quantile(.75)
iqr = q3 - q1
outl = {k: int(((df[df.Product_Category == k].Sales > q3[k] + 1.5 * iqr[k])).sum()) for k in order}
stats["box"] = dict(median=g.median().round(0).to_dict(), iqr=iqr.round(0).to_dict(), outliers=outl,
                    top=order[0], bottom=order[-1])

# 7. SCATTER: sales vs profit -------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.scatter(df.Sales, df.Profit, s=9, alpha=.35, color=BLUE, edgecolors="none")
k, b = np.polyfit(df.Sales, df.Profit, 1)
xs = np.linspace(df.Sales.min(), df.Sales.max(), 100)
ax.plot(xs, k * xs + b, color=ORANGE, lw=2.2, label=f"Trend line (slope = {k:.2f})")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1000:,.0f}K"))
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1000:,.0f}K"))
ax.set_title("Sales vs. profit per transaction"); ax.set_xlabel("Sales (₹ thousands)"); ax.set_ylabel("Profit (₹ thousands)")
ax.legend(frameon=False, loc="upper left")
save(fig, "07_scatter_sales_profit")
stats["sales_profit"] = dict(r=df.Sales.corr(df.Profit), slope=k, margin=df.Profit.sum() / df.Sales.sum() * 100,
                             loss_txns=int((df.Profit < 0).sum()))

# 8. SCATTER: discount vs profit -----------------------------------------------
d2 = df.dropna(subset=["Discount"])
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.scatter(d2.Discount, d2.Profit, s=9, alpha=.35, color=BLUE, edgecolors="none")
k2, b2 = np.polyfit(d2.Discount, d2.Profit, 1)
xs = np.linspace(0, .5, 50)
ax.plot(xs, k2 * xs + b2, color=ORANGE, lw=2.2, label=f"Trend line (r = {d2.Discount.corr(d2.Profit):.2f})")
ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=0))
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1000:,.0f}K"))
ax.set_title("Discount vs. profit per transaction"); ax.set_xlabel("Discount offered (%)"); ax.set_ylabel("Profit (₹ thousands)")
ax.legend(frameon=False, loc="upper right")
save(fig, "08_scatter_discount_profit")
d2b = d2.assign(bucket=pd.cut(d2.Discount, [0, .1, .2, .3, .4, .5], include_lowest=True))
mm = d2b.groupby("bucket", observed=True).apply(lambda t: t.Profit.sum() / t.Sales.sum() * 100)
stats["disc_profit"] = dict(r=d2.Discount.corr(d2.Profit), slope=k2, margin_low=mm.iloc[0], margin_high=mm.iloc[-1])

# 9. DONUT: sales share by segment ---------------------------------------------
sg = df.groupby("Customer_Segment")["Sales"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.2, 4.6))
wedges, _, autot = ax.pie(sg.values, colors=SEGMENT_COLORS, startangle=90, counterclock=False,
                          autopct="%1.1f%%", pctdistance=.78, wedgeprops=dict(width=.42, edgecolor="white", linewidth=2),
                          textprops=dict(color="white", fontweight="bold"))
ax.text(0, 0, f"Total\n{inr_m(sg.sum())}", ha="center", va="center", fontsize=12, fontweight="bold", color=INK)
ax.legend(wedges, [f"{k}  ({inr_m(v)})" for k, v in sg.items()], title="Customer segment",
          loc="center left", bbox_to_anchor=(1, .5), frameon=False)
ax.set_title("Share of total sales by customer segment")
save(fig, "09_donut_segment_share")
cnt = df.Customer_Segment.value_counts(normalize=True) * 100
stats["segment"] = dict(share=(sg / sg.sum() * 100).round(1).to_dict(), txn_share=cnt.round(1).to_dict(),
                        aov=df.groupby("Customer_Segment")["Sales"].mean().round(0).to_dict())

# 10. HEATMAP: correlation matrix ---------------------------------------------
cols = ["Sales", "Profit", "Discount", "Quantity", "Age", "Income"]
corr = df[cols].corr()
fig, ax = plt.subplots(figsize=(6.8, 5.4))
sns.heatmap(corr, annot=True, fmt=".2f", cmap=DIV, vmin=-1, vmax=1, center=0, linewidths=2, linecolor="white",
            square=True, cbar_kws=dict(label="Pearson correlation (r)", shrink=.8), ax=ax)
ax.grid(False); ax.set_title("Correlation between key numeric variables")
ax.set_xlabel(""); ax.set_ylabel("")
save(fig, "10_heatmap_correlation")
pairs = corr.where(np.triu(np.ones(corr.shape), 1).astype(bool)).stack()
stats["corr"] = dict(sales_profit=corr.loc["Sales", "Profit"], sales_qty=corr.loc["Sales", "Quantity"],
                     sales_disc=corr.loc["Sales", "Discount"], profit_disc=corr.loc["Profit", "Discount"],
                     sales_income=corr.loc["Sales", "Income"], sales_age=corr.loc["Sales", "Age"],
                     weakest=str(pairs.abs().idxmin()), weakest_val=pairs.loc[pairs.abs().idxmin()])

# 11. HEATMAP: avg sales, category x region -----------------------------------
pv = df.pivot_table(index="Product_Category", columns="Region", values="Sales", aggfunc="mean")
fig, ax = plt.subplots(figsize=(7.2, 4.6))
sns.heatmap(pv, annot=True, fmt=",.0f", cmap=SEQ, linewidths=2, linecolor="white",
            cbar_kws=dict(label="Average sales per transaction (₹)"), ax=ax)
ax.grid(False); ax.set_title("Average sales per transaction: category × region")
ax.set_xlabel("Region"); ax.set_ylabel("Product category")
save(fig, "11_heatmap_category_region")
st = pv.stack()
stats["pivot"] = dict(max_cell=str(st.idxmax()), max_val=st.max(), min_cell=str(st.idxmin()), min_val=st.min(),
                      cat_range={k: (pv.loc[k].max() - pv.loc[k].min()) / pv.loc[k].mean() * 100 for k in pv.index})

# 12. BAR: profit margin by category ------------------------------------------
pm = (df.groupby("Product_Category")["Profit"].sum() / df.groupby("Product_Category")["Sales"].sum() * 100).sort_values()
fig, ax = plt.subplots(figsize=(7.5, 4))
cols_ = [BLUE for k in pm.index]  # margins are near-identical, so no highlight
bars = ax.barh(pm.index, pm.values, color=cols_, height=.6)
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in pm.values], padding=3, fontsize=9)
ax.axvline(df.Profit.sum() / df.Sales.sum() * 100, color=GREY, ls="--", lw=1.5, label="Company average")
ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0)); ax.set_xlim(0, pm.max() * 1.2)
ax.grid(axis="y", visible=False); ax.legend(frameon=False, loc="upper right", bbox_to_anchor=(1, 1.12))
ax.set_title("Profit margin by product category"); ax.set_xlabel("Profit margin (% of sales)"); ax.set_ylabel("Product category")
save(fig, "12_bar_margin_by_category")
stats["margin"] = dict(pm.round(2).to_dict(), low=pm.idxmin(), high=pm.idxmax(), avg=df.Profit.sum() / df.Sales.sum() * 100)

# 13. BAR: return rate by delivery mode ---------------------------------------
rr = (df.assign(R=(df.Returned == "Yes")).groupby("Delivery_Mode")["R"].mean() * 100).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.5, 4))
cols_ = [BLUE for k in rr.index]  # rates are near-identical, so no highlight
bars = ax.bar(rr.index, rr.values, color=cols_, width=.55)
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in rr.values], padding=3, fontsize=9)
ax.axhline((df.Returned == "Yes").mean() * 100, color=GREY, ls="--", lw=1.5, label="Overall return rate")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0)); ax.set_ylim(0, rr.max() * 1.25)
ax.grid(axis="x", visible=False); ax.legend(frameon=False)
ax.set_title("Return rate by delivery mode"); ax.set_xlabel("Delivery mode"); ax.set_ylabel("Orders returned (%)")
save(fig, "13_bar_return_by_delivery")
stats["returns"] = dict(rr.round(2).to_dict(), overall=(df.Returned == "Yes").mean() * 100, high=rr.idxmax(), low=rr.idxmin())

# headline KPIs ---------------------------------------------------------------
stats["kpi"] = dict(total_sales=df.Sales.sum(), total_profit=df.Profit.sum(), margin=df.Profit.sum() / df.Sales.sum() * 100,
                    aov=df.Sales.mean(), rows=len(df), customers=df.Customer_ID.nunique())


def conv(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return str(o)


with open(f"{OUT}/stats.json", "w") as f:
    json.dump(stats, f, indent=2, default=conv)
print("charts written:", sorted(os.listdir(OUT)))
