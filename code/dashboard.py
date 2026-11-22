"""
Interactive sales dashboard (bonus). Author: Abhay Kumar Verma | Roll No: 2026M01410112
Run:  streamlit run dashboard.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st
from clean_data import load_and_clean

BLUE, ORANGE = "#2a78d6", "#eb6834"
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")


@st.cache_data
def get_data():
    return load_and_clean()


df = get_data()
st.title("Retail Sales Dashboard")
st.caption("Abhay Kumar Verma | Roll No: 2026M01410112")

# ---- filters (sidebar) ----
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Year", sorted(df.Year.unique()), default=sorted(df.Year.unique()))
regions = st.sidebar.multiselect("Region", sorted(df.Region.unique()), default=sorted(df.Region.unique()))
cats = st.sidebar.multiselect("Product category", sorted(df.Product_Category.unique()),
                              default=sorted(df.Product_Category.unique()))
segs = st.sidebar.multiselect("Customer segment", sorted(df.Customer_Segment.unique()),
                              default=sorted(df.Customer_Segment.unique()))
f = df[df.Year.isin(years) & df.Region.isin(regions) & df.Product_Category.isin(cats) & df.Customer_Segment.isin(segs)]
if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"₹{f.Sales.sum()/1e6:,.2f}M")
k2.metric("Total Profit", f"₹{f.Profit.sum()/1e6:,.2f}M")
k3.metric("Profit Margin", f"{f.Profit.sum()/f.Sales.sum()*100:.1f}%")
k4.metric("Average Order Value", f"₹{f.Sales.mean():,.0f}")

# ---- charts ----
c1, c2 = st.columns(2)
m = f.groupby("Month", as_index=False)["Sales"].sum()
fig = px.line(m, x="Month", y="Sales", markers=True, title="Monthly sales", color_discrete_sequence=[BLUE])
fig.update_layout(yaxis_title="Total sales (₹)", xaxis_title="Order month")
c1.plotly_chart(fig, width="stretch")

cat = f.groupby("Product_Category", as_index=False)["Sales"].sum().sort_values("Sales")
fig = px.bar(cat, x="Sales", y="Product_Category", orientation="h", title="Sales by product category",
             color_discrete_sequence=[BLUE])
fig.update_layout(xaxis_title="Total sales (₹)", yaxis_title="Product category")
c2.plotly_chart(fig, width="stretch")

c3, c4 = st.columns(2)
reg = f.groupby("Region", as_index=False)["Sales"].sum()
reg["Lowest"] = reg.Sales == reg.Sales.min()
fig = px.bar(reg, x="Region", y="Sales", color="Lowest", title="Sales by region (lowest highlighted)",
             color_discrete_map={True: ORANGE, False: BLUE})
fig.update_layout(showlegend=False, yaxis_title="Total sales (₹)")
c3.plotly_chart(fig, width="stretch")

seg = f.groupby("Customer_Segment", as_index=False)["Sales"].sum()
fig = px.pie(seg, names="Customer_Segment", values="Sales", hole=.5, title="Sales share by customer segment",
             color_discrete_sequence=[BLUE, ORANGE, "#1baf7a"])
c4.plotly_chart(fig, width="stretch")

pv = f.pivot_table(index="Product_Category", columns="Region", values="Sales", aggfunc="mean")
fig = px.imshow(pv, text_auto=",.0f", color_continuous_scale="Blues", aspect="auto",
                title="Average sales per transaction: category × region")
st.plotly_chart(fig, width="stretch")
