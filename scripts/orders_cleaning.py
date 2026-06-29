#!/usr/bin/env python
# coding: utf-8

import pandas as pd


df = pd.read_csv("../Data/raw/orders.csv")


# Data exploration

df.head()

df.dtypes

df.info()

df.describe()

df.isnull().mean() * 100

df["order_status"].value_counts(dropna=False)


# Data correction

df["order_status"] = df["order_status"].str.title()

df["order_status"].value_counts(dropna=False)

df.groupby("order_status")["actual_delivery_date"].apply(lambda x: x.isnull().mean() * 100)


# Null values

df.isnull().sum()

df["profit_margin_pct"] = df["profit_margin_pct"].fillna(
    (df["gross_margin_usd"] / df["order_value_usd"]) * 100
)

(df == "").sum()

placeholders = [
    "NA", "N/A", "NULL", "null", "None", "none",
    "-", "--", "?", "Unknown", "unknown"
]

df.isin(placeholders).sum()

df[["customer_id", "customer_name", "customer_country", "customer_segment"]].isnull().sum()

df[["shipment_id", "warehouse_id"]].isnull().sum()

df.groupby("order_status")[["shipment_id", "warehouse_id"]].apply(lambda x: x.isnull().mean() * 100)

df["return_reason"] = df["return_reason"].fillna("Not Returned")
df["warehouse_id"] = df["warehouse_id"].fillna("UNKNOWN")
df["shipment_id"] = df["shipment_id"].fillna("NO_SHIPMENT")

df.isnull().sum()


# Duplicates

df.duplicated().sum()

df["order_id"].duplicated().sum()

df[df["order_id"].duplicated(keep=False)].sort_values("order_id")

df.groupby("order_id")["product_id"].nunique().sort_values(ascending=False).head(10)

df["shipment_id"].duplicated().sum()

df.groupby("shipment_id")["order_id"].nunique().sort_values(ascending=False).head(10)


# Dates

date_cols = [
    "order_date",
    "promised_delivery_date",
    "actual_delivery_date"
]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")

df[date_cols].isnull().sum()

(df["actual_delivery_date"] < df["order_date"]).sum()

df[df["actual_delivery_date"] < df["order_date"]][
    ["order_id", "order_date", "actual_delivery_date", "order_status"]
].head(20)

mask = df["order_date"] > df["actual_delivery_date"]

df.loc[mask, "actual_delivery_date"] = pd.NaT
df.loc[mask, "promised_delivery_date"] = pd.NA

df["delivery_delay_days"] = (
    df["actual_delivery_date"] - df["promised_delivery_date"]
).dt.days


# Text standardization

df["order_status"].unique()

df["customer_country"].unique()

df["customer_segment"].unique()


# Numeric validation

num_cols = df.select_dtypes(include="number").columns

num_cols.drop("delivery_delay_days")

for col in num_cols:
    print(col, (df[col] < 0).sum())

df["order_value_usd"] = df["order_value_usd"].abs()

df["order_quantity"].describe()

df["profit_margin_pct"].describe()

df["discount_pct"].max()

df["discount_pct"].min()

df["profit_margin_pct"].isnull().sum()


# Final preview

df.head()


# Save cleaned data

df.to_csv("../data/cleaned/orders_cleaned.csv", index=False)