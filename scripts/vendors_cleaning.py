#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


df = pd.read_csv("../Data/raw/vendors.csv")


# Data exploration

df.head()

df.dtypes

df.info()

df.describe()


# Missing values

df.isnull().sum()

df["snapshot_month"] = pd.to_datetime(df["snapshot_month"])
df["contract_start_date"] = pd.to_datetime(df["contract_start_date"])
df["contract_expiry_date"] = pd.to_datetime(df["contract_expiry_date"])

df["quality_acceptance_rate"] = df["quality_acceptance_rate"].fillna(
    df.groupby("vendor_id")["quality_acceptance_rate"]
    .transform(lambda x: x.rolling(3, min_periods=1).mean())
)

df["quality_acceptance_rate"] = df["quality_acceptance_rate"].fillna(
    df.groupby("vendor_category")["quality_acceptance_rate"].transform("median")
)

df["financial_stability_score"] = df["financial_stability_score"].fillna(
    df.groupby("vendor_category")["financial_stability_score"].transform("median")
)

df.isnull().sum()

vris_components = [
    "on_time_delivery_rate",
    "quality_acceptance_rate",
    "invoice_accuracy_rate",
    "financial_stability_score",
    "esg_compliance_score"
]

df["vris_score"] = df["vris_score"].fillna(
    df[vris_components].mean(axis=1)
)


# Duplicates

df.duplicated().sum()

df["vendor_record_id"].duplicated().sum()

df.duplicated(subset=["vendor_id", "snapshot_month"]).sum()

df["vendor_id"].isnull().sum()


# Dates

date_cols = [
    "snapshot_month",
    "contract_start_date",
    "contract_expiry_date"
]

cutoff_date = pd.Timestamp("2024-12-31")

for col in date_cols:
    print(col, (df[col] > cutoff_date).sum())


# Text cleanup

text_cols = df.select_dtypes(include="object").columns

for col in text_cols:
    df[col] = df[col].str.strip()


# Financial checks

financial_cols = [
    "procurement_spend_usd",
    "payment_terms_days",
    "days_payable_outstanding"
]

for col in financial_cols:
    print(col, (df[col] < 0).sum())

df[df["days_payable_outstanding"] < 0][
    ["vendor_id", "snapshot_month", "payment_terms_days", "days_payable_outstanding"]
].head(20)

df.loc[df["days_payable_outstanding"] < 0, "days_payable_outstanding"] = np.nan

df["days_payable_outstanding"] = df["days_payable_outstanding"].fillna(
    df.groupby("vendor_category")["days_payable_outstanding"].transform("median")
)


# Score checks

score_cols = [
    "on_time_delivery_rate",
    "quality_acceptance_rate",
    "defect_rate_pct",
    "invoice_accuracy_rate",
    "concentration_risk_pct",
    "financial_stability_score",
    "esg_compliance_score",
    "vris_score"
]

for col in score_cols:
    print(col, ((df[col] < 0) | (df[col] > 100)).sum())


# Binary checks

binary_cols = [
    "active_dispute_flag",
    "preferred_vendor_flag"
]

for col in binary_cols:
    print(df[col].value_counts(dropna=False))
    print()


# Final duplicate check

df.duplicated(subset=["vendor_id", "snapshot_month"]).sum()


# Save cleaned data

df.to_csv("../data/cleaned/vendors_cleaned.csv", index=False)