#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


df = pd.read_csv("../Data/raw/financials.csv")


# Data exploration

df.head()

df.dtypes

df.info()

df.describe()


# Missing values

df.isnull().sum()

current_assets = (
    df["accounts_receivable_usd"] +
    df["inventory_value_usd"] +
    df["cash_position_usd"]
)

current_liabilities = df["accounts_payable_usd"]

calculated_ratio = current_assets / current_liabilities.replace(0, np.nan)

df["working_capital_ratio"] = df["working_capital_ratio"].fillna(calculated_ratio)


risk_components = [
    "working_capital_ratio",
    "days_sales_outstanding",
    "days_payable_outstanding",
    "cash_conversion_cycle"
]

ranked = df[risk_components].rank(pct=True) * 100

# Lower working capital ratio = higher risk
ranked["working_capital_ratio"] = 100 - ranked["working_capital_ratio"]

calculated_risk_score = ranked.mean(axis=1)

df["financial_risk_score"] = df["financial_risk_score"].fillna(calculated_risk_score)

df["financial_risk_score"] = df["financial_risk_score"].clip(0, 100)


# Duplicates

df.duplicated().sum()

df = df.drop_duplicates()

df.duplicated().sum()

df["finance_record_id"].duplicated().sum()


# Dates

df["record_date"] = pd.to_datetime(df["record_date"], errors="coerce")

(df["record_date"] > pd.Timestamp("2024-12-31")).sum()

(df["record_date"] < pd.Timestamp("2021-01-01")).sum()


# Text columns

text_cols = df.select_dtypes(include="object").columns

for col in text_cols:
    df[col] = df[col].str.strip()


# Numeric columns

numeric_cols = df.select_dtypes(include="number").columns

for col in numeric_cols:
    print(col, (df[col] < 0).sum())


# Save cleaned data

df.to_csv("../data/cleaned/financials_cleaned.csv", index=False)