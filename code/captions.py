"""
Insight captions for every chart. All numbers come from charts/stats.json
(produced by generate_charts.py), so captions always match the charts.
Author: Abhay Kumar Verma | Roll No: 2026M01410112
"""
import json
import calendar


def m(x):  # rupees in millions
    return f"₹{x/1e6:,.1f}M"


def build():
    s = json.load(open("charts/stats.json"))
    L, R, C, A, I, B, SP, DP, SG, CO, PV, MG, RT = (s[k] for k in
        ["line", "region", "category", "age", "income", "box", "sales_profit", "disc_profit",
         "segment", "corr", "pivot", "margin", "returns"])
    mon = lambda d: calendar.month_abbr[int(d[5:7])] + " " + d[:4]
    furn_elec = (C["Electronics"] + C["Furniture"]) / R["total"] * 100

    return [
        dict(section="1. Overall sales trend", file="01_line_monthly_sales",
             title="Figure 1: Monthly sales, Jan 2023 – Dec 2024",
             caption=(f"Sales were essentially flat across the two years: {m(L['y2023'])} in 2023 versus {m(L['y2024'])} in 2024 "
                      f"({L['growth']:+.1f}%). Month-to-month swings are large (peak {mon(L['peak'])} at {m(L['peak_val'])}, "
                      f"low {mon(L['low'])} at {m(L['low_val'])}) but show no clear trend or repeating seasonal pattern. "
                      "Leadership should treat the business as stable but not growing, and look for growth levers elsewhere.")),
        dict(section="2. Where sales come from", file="02_bar_sales_by_region",
             title="Figure 2: Total sales by region",
             caption=(f"{R['top']} leads with {m(R[R['top']])}, while {R['bottom']} (highlighted) trails at {m(R[R['bottom']])}, "
                      f"a gap of {R['gap_pct']:.0f}%. The four regions are fairly close, so no region is failing. "
                      f"{R['bottom']} is still the clearest candidate for a targeted sales push.")),
        dict(section="2. Where sales come from", file="03_bar_sales_by_category",
             title="Figure 3: Total sales by product category",
             caption=(f"{C['top']} alone brings in {C['top_share']:.0f}% of all sales, and with Furniture the two categories make up "
                      f"{furn_elec:.0f}% of revenue. {C['bottom']} contributes only {C['bottom_share']:.1f}%. "
                      "The business depends heavily on two high-ticket categories, so stock and marketing there matter most.")),
        dict(section="3. Who the customers are", file="04_hist_age",
             title="Figure 4: Distribution of customer age",
             caption=(f"Ages range from {A['min']:.0f} to {A['max']:.0f} and cluster around the mean of {A['mean']:.1f} "
                      f"(median {A['median']:.0f}). Skewness is only {A['skew']:.2f}, so the distribution is almost symmetric. "
                      f"About {A['share_25_45']:.0f}% of transactions come from customers aged 25–45, which is the core audience for campaigns.")),
        dict(section="3. Who the customers are", file="05_hist_income",
             title="Figure 5: Distribution of customer income",
             caption=(f"Income is right-skewed: the mean (₹{I['mean']:,.0f}) sits above the median (₹{I['median']:,.0f}) because a few high earners "
                      f"pull the average up. Skewness is {I['skew_capped']:.2f} even after capping at the 99th percentile "
                      f"(₹{I['cap']:,.0f}); the raw data reaches ₹{I['raw_max']:,.0f}. "
                      "Most customers earn modestly, so pricing and offers should target the middle of the range, not the average.")),
        dict(section="3. Who the customers are", file="09_donut_segment_share",
             title="Figure 6: Share of total sales by customer segment",
             caption=(f"Consumers generate {SG['share']['Consumer']:.0f}% of sales, Corporate {SG['share']['Corporate']:.0f}% and "
                      f"Home Office {SG['share']['Home Office']:.0f}%. Average order values are very similar across segments "
                      f"(₹{min(SG['aov'].values()):,.0f}–₹{max(SG['aov'].values()):,.0f}), so each segment's share simply follows how many orders it places. "
                      "Order volume, not order size, is what separates the segments.")),
        dict(section="4. Spread, outliers and profit", file="06_box_sales_by_category",
             title="Figure 7: Sales per transaction by product category",
             caption=(f"Typical order value differs by more than 15 times across categories, from a median of ₹{B['median']['Furniture']:,.0f} "
                      f"for Furniture to ₹{B['median']['Grocery']:,.0f} for Grocery. Furniture and Electronics also have the widest spread, "
                      f"and Electronics has the most high-value outliers ({B['outliers']['Electronics']}). "
                      "Big-ticket orders in these categories drive revenue, so they deserve special handling in delivery and returns.")),
        dict(section="4. Spread, outliers and profit", file="12_bar_margin_by_category",
             title="Figure 8: Profit margin by product category",
             caption=(f"Margins are almost identical across categories, between {min(MG[k] for k in ['Clothing','Office Supplies','Grocery','Furniture','Electronics']):.1f}% "
                      f"and {max(MG[k] for k in ['Clothing','Office Supplies','Grocery','Furniture','Electronics']):.1f}%, close to the company average of {MG['avg']:.1f}%. "
                      "So no category is losing money; profit differences come from sales volume, not from pricing or cost problems. "
                      "That is why Electronics and Furniture produce most of the profit.")),
        dict(section="5. Relationships between variables", file="07_scatter_sales_profit",
             title="Figure 9: Sales vs. profit per transaction",
             caption=(f"Sales and profit move almost in lockstep (r = {SP['r']:.2f}); each extra rupee of sales adds about "
                      f"₹{SP['slope']:.2f} of profit. No transaction in the cleaned data made a loss, and the overall margin is {SP['margin']:.1f}%. "
                      "Because the relationship is linear and tight, growing sales is the reliable way to grow profit.")),
        dict(section="5. Relationships between variables", file="08_scatter_discount_profit",
             title="Figure 10: Discount vs. profit per transaction",
             caption=(f"There is only a weak negative link between discount and profit (r = {DP['r']:.2f}), and the points form a shapeless cloud. "
                      f"Margin is {DP['margin_low']:.1f}% for the smallest discounts and {DP['margin_high']:.1f}% for the largest. "
                      "In this data, deeper discounts do not visibly reduce margin, so they should be judged by whether they lift sales volume.")),
        dict(section="5. Relationships between variables", file="13_bar_return_by_delivery",
             title="Figure 11: Return rate by delivery mode",
             caption=(f"About {RT['overall']:.1f}% of orders are returned, and the rate hardly changes with delivery mode "
                      f"({RT['low']} {RT[RT['low']]:.1f}% to {RT['high']} {RT[RT['high']]:.1f}%). "
                      "Faster or slower delivery is not driving returns, so reducing returns will need other levers such as product quality or descriptions.")),
        dict(section="6. Combined heatmap views", file="10_heatmap_correlation",
             title="Figure 12: Correlation between key numeric variables",
             caption=(f"Sales and profit are strongly correlated ({CO['sales_profit']:.2f}), and quantity has a moderate link to both "
                      f"({CO['sales_qty']:.2f}). Discount, age and income are almost unrelated to sales (all within ±0.12). "
                      "Customer age and income do not explain spending here, so order quantity and product mix are the better levers.")),
        dict(section="6. Combined heatmap views", file="11_heatmap_category_region",
             title="Figure 13: Average sales per transaction, category × region",
             caption=(f"The product category matters far more than the region: the best cell is {PV['max_cell'].replace('(','').replace(')','').replace(chr(39),'')} "
                      f"at ₹{PV['max_val']:,.0f}, and the weakest is {PV['min_cell'].replace('(','').replace(')','').replace(chr(39),'')} at ₹{PV['min_val']:,.0f}. "
                      f"Within any one category, average sales differ by only {min(PV['cat_range'].values()):.0f}–{max(PV['cat_range'].values()):.0f}% across regions. "
                      "Regional strategy can stay broadly uniform; product strategy is where the real differences lie.")),
    ]


if __name__ == "__main__":
    for c in build():
        print(c["title"], "\n ", c["caption"], "\n")
