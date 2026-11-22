# Data Visualization: Retail Sales Visual Story

**Name:** Abhay Kumar Verma  
**Roll No:** 2026M01410112  
**Project:** Project 2, Data Visualization (Data Analyst Training Program)

## What this project does
Cleans the retail transaction dataset (2023–2024, India) and produces 13 charts (line, bar, histogram, box plot,
scatter, donut, heatmap) with business insight captions, a Word report, and a Streamlit dashboard (bonus).

## Files
| File | Purpose |
|---|---|
| `data/retail_customer_sales_dataset.csv` | Raw dataset |
| `clean_data.py` | Cleaning: duplicates, mixed dates, labels, invalid values, income cap |
| `generate_charts.py` | Generates all 13 charts into `charts/` and writes `charts/stats.json` |
| `captions.py` | Insight captions built from the computed statistics |
| `2026M01410112_AbhayKumarVerma_DataVisualization.ipynb` | Notebook with all code, charts and captions |
| `build_notebook.py` | Builds the notebook from the chart code and captions |
| `dashboard.py` | Streamlit dashboard: 4 KPIs, 4 filters |
| `report/2026M01410112_AbhayKumarVerma_DataVisualization_Report.docx` | Final visual report (also as PDF) |

## How to run
```bash
pip install -r requirements.txt
python generate_charts.py          # creates charts/*.png
jupyter notebook 2026M01410112_AbhayKumarVerma_DataVisualization.ipynb
streamlit run dashboard.py         # interactive dashboard
```

## Data cleaning summary
7,084 raw rows became 7,000: duplicates removed; four date formats parsed; Region/Gender labels standardised;
invalid Age and Discount set to missing; Delivery_Date earlier than Order_Date set to missing; Income capped at the 99th
percentile for plotting only.
