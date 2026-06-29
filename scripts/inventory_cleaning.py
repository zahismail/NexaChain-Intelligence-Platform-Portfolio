#!/usr/bin/env python
# coding: utf-8

import pandas as pd


df = pd.read_csv("../Data/raw/inventory.csv")


# Data exploration

df.head()

df.info()

df.shape


# Missing values

df.isnull().sum()

(df == "").sum()

placeholders = [
    "NA", "N/A", "NULL", "null", "None", "none",
    "-", "--", "?", "Unknown", "unknown"
]

df.isin(placeholders).sum()

df["vendor_lead_time_days"] = df.groupby("vendor_id")["vendor_lead_time_days"].transform(lambda x: x.fillna(x.mean()))
df["reorder_point"] = df.groupby("product_category")["reorder_point"].transform(lambda x: x.fillna(x.median()))


# Duplicates

df.duplicated().sum()

df["inventory_id"].duplicated().sum()


# ID cleanup

df["warehouse_id"].value_counts(dropna=False)

df["warehouse_id"] = df["warehouse_id"].str.strip().str.upper()
df["product_id"] = df["product_id"].str.strip().str.upper()
df["vendor_id"] = df["vendor_id"].str.strip().str.upper()


# Data types

df.dtypes

date_cols = [
    "snapshot_date",
    "last_receipt_date",
    "last_issue_date"
]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")


# Value checks

df["safety_stock_units"].isnull().sum()

(df["safety_stock_units"] < 0).sum()

(df["unit_cost_usd"] < 0).sum()


# Outliers

outlier_cols = [
    "stock_on_hand",
    "units_reserved",
    "available_stock",
    "reorder_point",
    "reorder_quantity",
    "safety_stock_units",
    "max_stock_level",
    "days_of_supply",
    "vendor_lead_time_days",
    "stock_age_days",
    "holding_cost_rate_pct",
    "unit_cost_usd",
    "total_inventory_value_usd"
]

for col in outlier_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower) | (df[col] > upper)]

    print(col, ":", len(outliers), "outliers")


# ID checks

df[["inventory_id", "product_id", "warehouse_id", "vendor_id"]].isnull().sum()


# Stock checks

stock_cols = [
    "stock_on_hand",
    "units_reserved",
    "available_stock",
    "reorder_point",
    "reorder_quantity",
    "safety_stock_units",
    "max_stock_level"
]

for col in stock_cols:
    print(col, (df[col] < 0).sum())

df.loc[df["stock_on_hand"] < 0, "stock_on_hand"] = 0

print("stock_on_hand", (df["stock_on_hand"] < 0).sum())


# Cost checks

cost_cols = [
    "unit_cost_usd",
    "total_inventory_value_usd",
    "holding_cost_rate_pct"
]

for col in cost_cols:
    print(col, (df[col] < 0).sum())


# Categorical checks

df["stockout_flag"].value_counts(dropna=False)

df["product_category"].nunique()


# Date checks

cutoff_date = pd.Timestamp("2024-12-31")

(df["snapshot_date"] > cutoff_date).sum()

(df["last_receipt_date"] > df["snapshot_date"]).sum()

(df["last_issue_date"] > df["snapshot_date"]).sum()


# Save cleaned data

df.to_csv("../data/cleaned/inventory_cleaned.csv", index=False)