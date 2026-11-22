"""
Data cleaning for the Retail Sales Data Visualization project.
Author: Abhay Kumar Verma | Roll No: 2026M01410112

Minimal cleaning so that charts are not distorted by bad data:
  1. remove duplicate records
  2. parse mixed date formats
  3. standardise Region / Gender labels
  4. set impossible Age / Discount values to NaN
  5. cap extreme Income outliers (for plotting only; flag column kept)
"""
import re
import pandas as pd
import numpy as np

RAW_PATH = "data/retail_customer_sales_dataset.csv"

REGION_MAP = {
    "north": "North", "nort": "North",
    "south": "South", "sth": "South",
    "east": "East",
    "west": "West",
}
GENDER_MAP = {"male": "Male", "m": "Male", "female": "Female", "f": "Female"}


def parse_dates(series: pd.Series) -> pd.Series:
    """Parse the four date layouts found in the file (ISO, dd/mm/yyyy,
    mm-dd-yyyy, dd-Mon-yyyy). Checked against the data: values with "/" are
    day/month, values with "-" are month-day (first part never exceeds 12)."""
    s = series.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    iso = s.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
    slash = s.str.match(r"^\d{2}/\d{2}/\d{4}$", na=False)
    dash = s.str.match(r"^\d{2}-\d{2}-\d{4}$", na=False)
    mon = s.str.match(r"^\d{2}-[A-Za-z]{3}-\d{4}$", na=False)
    out[iso] = pd.to_datetime(s[iso], format="%Y-%m-%d")
    out[slash] = pd.to_datetime(s[slash], format="%d/%m/%Y")
    out[dash] = pd.to_datetime(s[dash], format="%m-%d-%Y")
    out[mon] = pd.to_datetime(s[mon], format="%d-%b-%Y")
    return out


def load_and_clean(path: str = RAW_PATH, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_csv(path)
    log = {"raw_rows": len(df)}

    # 1. duplicates: exact duplicate rows first, then repeated Transaction_ID
    df = df.drop_duplicates()
    log["after_exact_dups"] = len(df)
    df = df.drop_duplicates(subset="Transaction_ID", keep="first")
    log["after_id_dups"] = len(df)

    # 2. dates
    df["Order_Date"] = parse_dates(df["Order_Date"])
    df["Delivery_Date"] = parse_dates(df["Delivery_Date"])
    bad_delivery = df["Delivery_Date"] < df["Order_Date"]
    log["delivery_before_order"] = int(bad_delivery.sum())
    df.loc[bad_delivery, "Delivery_Date"] = pd.NaT
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()

    # 3. category labels
    df["Region"] = df["Region"].str.strip().str.lower().map(REGION_MAP)
    df["Gender"] = df["Gender"].str.strip().str.lower().map(GENDER_MAP)

    # 4. impossible values
    bad_age = (df["Age"] < 18) | (df["Age"] > 100)
    log["invalid_age"] = int(bad_age.sum())
    df.loc[bad_age, "Age"] = np.nan
    bad_disc = (df["Discount"] < 0) | (df["Discount"] > 0.5)
    log["invalid_discount"] = int(bad_disc.sum())
    df.loc[bad_disc, "Discount"] = np.nan

    # 5. income outliers: cap at the 99th percentile for plotting
    cap = df["Income"].quantile(0.99)
    df["Income_Capped"] = df["Income"].clip(upper=cap)
    log["income_cap_99pct"] = round(float(cap), 2)

    log["final_rows"] = len(df)
    if verbose:
        for k, v in log.items():
            print(f"{k:>24}: {v}")
    return df


if __name__ == "__main__":
    d = load_and_clean(verbose=True)
    print(d.isna().sum()[d.isna().sum() > 0])
    print(d.Order_Date.min(), d.Order_Date.max())
    print(d.Region.value_counts().to_dict(), d.Gender.value_counts().to_dict())
