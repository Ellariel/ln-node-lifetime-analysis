import os, sys
import numpy as np
import pandas as pd


def log_transform(x):
    return np.sign(x) * np.log10(1 + np.abs(x))


base_dir = os.path.dirname(__file__)
if "app" in base_dir:
    base_dir = "./"

data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))
results_dir = os.path.abspath(os.path.join(base_dir, "..", "results"))
os.makedirs(results_dir, exist_ok=True)

print("data_dir:", data_dir)
print("results_dir:", results_dir)

gdp_cap = (
    pd.read_csv(
        os.path.join(data_dir, "gdp-per-capita-world-bank.csv"),
        low_memory=False,
        na_values=[".."],
    )
    .rename(columns={"Country Name": "country_name", "Country Code": "country_id"})
    .drop_duplicates()
).dropna(subset=["country_id"])
gdp_cap["gdp_cap"] = gdp_cap[gdp_cap.columns[4:]].mean(axis=1)
gdp_cap = gdp_cap[["country_name", "country_id", "gdp_cap"]]

code2 = (
    pd.read_csv(
        os.path.join(data_dir, "wikipedia-iso-country-codes.csv"),  # low_memory=False
    ).rename(
        columns={
            "English short name lower case": "country_name",
            "Alpha-3 code": "country_id",
            "Alpha-2 code": "country",
        }
    )
)[["country_id", "country"]]

c_data = pd.merge(gdp_cap, code2, on=["country_id"], how="left")
c_data = c_data[["country", "gdp_cap"]].dropna(subset=["country"])
c_data["log_gdp_cap"] = log_transform(c_data["gdp_cap"])

df = pd.read_csv(os.path.join(data_dir, "geo_nodes.csv"), sep=";")
df["log_mean_degree"] = log_transform(df["mean_degree"])
df["log_lifetime"] = log_transform(df["lifetime"])
df["log_mean_shared_capacity"] = log_transform(df["mean_shared_capacity"])

f_data = pd.merge(df, c_data, on=["country"], how="left").drop(["node"], axis=1)
print(f"Number of items: {len(f_data)}")  # 39159
f_data.to_csv(os.path.join(results_dir, "data.csv"), index=True)
