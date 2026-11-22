"""Builds the Jupyter notebook from generate_charts.py + captions.py (run once)."""
import re, json
import nbformat as nbf
from captions import build

ROLL, NAME = "2026M01410112", "Abhay Kumar Verma"
src = open("generate_charts.py").read()
caps = {c["file"][:2]: c for c in build()}

head, *rest = re.split(r"(?m)^# (?=\d+\. [A-Z]+:)", src)
head = head.split('"""', 2)[2].lstrip("\n")
head = head.replace('matplotlib.use("Agg")\n', "").replace("    plt.close(fig)\n", "    plt.show()\n    plt.close(fig)\n")
head = head.replace("import json\nimport os", "import json\nimport os\nimport warnings\nwarnings.filterwarnings('ignore')")

nb = nbf.v4.new_notebook()
C = nb.cells
C.append(nbf.v4.new_markdown_cell(
    f"# Data Visualization: Turning Retail Sales Data into a Visual Story\n"
    f"**Name:** {NAME}  |  **Roll No:** {ROLL}\n\n"
    "**Project 2, Data Analyst Training Program.** This notebook cleans the retail dataset and generates all charts "
    "used in the report (13 charts covering line, bar, histogram, box plot, scatter, donut and heatmap). "
    "Run it from the project root so `data/` and `clean_data.py` are found."))
C.append(nbf.v4.new_markdown_cell("## 1. Setup, cleaning and palette\nOne consistent palette is used everywhere: blue for normal data, orange to highlight the point being made, grey for reference lines."))
C.append(nbf.v4.new_code_cell(head.strip()))
C.append(nbf.v4.new_markdown_cell(
    "### Data cleaning summary\n`clean_data.py` removes duplicates, parses the four mixed date formats, standardises Region/Gender labels, "
    "blanks impossible Age (<18 or >100) and Discount (outside 0–0.5) values, and caps Income at the 99th percentile for plotting."))
C.append(nbf.v4.new_code_cell(
    "raw = pd.read_csv('data/retail_customer_sales_dataset.csv')\n"
    "print('Raw shape  :', raw.shape)\nprint('Clean shape:', df.shape)\n"
    "_ = load_and_clean(verbose=True)\n"
    "print('\\nRegions:', sorted(df.Region.unique()), '| Genders:', sorted(df.Gender.unique()))\n"
    "print('Date range:', df.Order_Date.min().date(), 'to', df.Order_Date.max().date())\n"
    "df.head()"))
C.append(nbf.v4.new_markdown_cell("## 2. Charts"))
for sec in rest:
    code = sec
    num = re.match(r"(\d+)\.", sec).group(1).zfill(2)
    title = sec.split("\n")[0]
    if title.startswith("12.") or True:
        pass
    if "# headline KPIs" in code:
        code, tail = code.split("# headline KPIs", 1)
        tail = "# headline KPIs" + tail
    else:
        tail = None
    C.append(nbf.v4.new_markdown_cell(f"### Chart {title.split(':')[0].replace('.', '')}: {title.split(':',1)[1].strip().capitalize() if ':' in title else title}"))
    C.append(nbf.v4.new_code_cell("# " + code.strip()))
    if num in caps:
        c = caps[num]
        C.append(nbf.v4.new_markdown_cell(f"**{c['title']}**\n\n*Insight:* {c['caption']}"))
    if tail:
        C.append(nbf.v4.new_markdown_cell("## 3. Headline KPIs and saved statistics"))
        C.append(nbf.v4.new_code_cell(tail.strip() + "\npd.Series(stats['kpi'])"))
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
fn = f"{ROLL}_AbhayKumarVerma_DataVisualization.ipynb"
nbf.write(nb, fn)
print(fn, len(C), "cells")
