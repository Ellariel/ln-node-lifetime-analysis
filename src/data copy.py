import os, sys
import numpy as np
import pandas as pd


base_dir = os.path.dirname(__file__)
if "app" in base_dir:
    base_dir = "./"

data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))
results_dir = os.path.abspath(os.path.join(base_dir, "..", "results"))
os.makedirs(results_dir, exist_ok=True)

print("data_dir:", data_dir)
print("results_dir:", results_dir)


def log_transform(x):
    return np.sign(x) * np.log10(1 + np.abs(x))


hdi = (
    pd.read_excel(
        os.path.join(data_dir, "hdi-trends.xlsx"), skiprows=4, na_values=[".."]
    )
    .rename(columns={"Country": "country_name"})[
        ["country_name", 2020, 2021, 2022, 2023]
    ]
    .dropna(subset=[2020])
)
hdi["hdi"] = hdi[hdi.columns[1:]].mean(axis=1)
hdi = hdi[["country_name", "hdi"]]

hdi.loc[hdi["country_name"] == "Bahamas", "country_name"] = "Bahamas, The"
hdi.loc[hdi["country_name"] == "Bolivia (Plurinational State of)", "country_name"] = (
    "Bolivia"
)
hdi.loc[hdi["country_name"] == "Congo (Democratic Republic of the)", "country_name"] = (
    "Congo, Rep."
)
hdi.loc[hdi["country_name"] == "Congo", "country_name"] = "Congo, Dem. Rep."
hdi.loc[hdi["country_name"] == "Côte d'Ivoire", "country_name"] = "Cote d'Ivoire"
hdi.loc[hdi["country_name"] == "Egypt", "country_name"] = "Egypt, Arab Rep."
hdi.loc[hdi["country_name"] == "Gambia", "country_name"] = "Gambia, The"
hdi.loc[hdi["country_name"] == "Hong Kong, China (SAR)", "country_name"] = (
    "Hong Kong SAR, China"
)
hdi.loc[hdi["country_name"] == "Iran (Islamic Republic of)", "country_name"] = (
    "Iran, Islamic Rep."
)
hdi.loc[hdi["country_name"] == "Korea (Republic of)", "country_name"] = "Korea, Rep."
hdi.loc[hdi["country_name"] == "Kyrgyzstan", "country_name"] = "Kyrgyz Republic"
hdi.loc[hdi["country_name"] == "Lao People's Democratic Republic", "country_name"] = (
    "Lao PDR"
)
hdi.loc[hdi["country_name"] == "Micronesia (Federated States of)", "country_name"] = (
    "Micronesia, Fed. Sts."
)
hdi.loc[hdi["country_name"] == "Slovakia", "country_name"] = "Slovak Republic"
hdi.loc[hdi["country_name"] == "Tanzania (United Republic of)", "country_name"] = (
    "Tanzania"
)
hdi.loc[hdi["country_name"] == "Venezuela (Bolivarian Republic of)", "country_name"] = (
    "Venezuela, RB"
)
hdi.loc[hdi["country_name"] == "Eswatini (Kingdom of)", "country_name"] = "Eswatini"
hdi.loc[hdi["country_name"] == "Yemen", "country_name"] = "Yemen, Rep."
hdi.loc[hdi["country_name"] == "Moldova (Republic of)", "country_name"] = "Moldova"
hdi.loc[hdi["country_name"] == "Türkiye", "country_name"] = "Turkiye"


gini = (
    pd.read_csv(
        os.path.join(data_dir, "gini-world-bank.csv"),
        low_memory=False,
        na_values=[".."],
    )
    .rename(columns={"Country Name": "country_name", "Country Code": "country_id"})
    .drop_duplicates()
).dropna(subset=["country_id"])
gini["gini"] = gini[gini.columns[4:]].mean(axis=1)
gini = gini[["country_name", "country_id", "gini"]]

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
        os.path.join(data_dir, "wikipedia-iso-country-codes.csv"), low_memory=False
    ).rename(
        columns={
            "English short name lower case": "country_name",
            "Alpha-3 code": "country_id",
            "Alpha-2 code": "country",
        }
    )
)[["country_id", "country"]]

c_data = pd.merge(gdp_cap, gini, on=["country_name", "country_id"], how="outer")
c_data = pd.merge(c_data, hdi, on=["country_name"], how="outer")
c_data = pd.merge(c_data, code2, on=["country_id"], how="left")
c_data = c_data[["country", "gdp_cap", "gini", "hdi"]].dropna(subset=["country"])
c_data["log_gdp_cap"] = log_transform(c_data["gdp_cap"])
# c_data.to_csv(os.path.join(data_dir, "vars.csv"), index=False)

df = pd.read_csv(os.path.join(data_dir, "geo_nodes.csv"))
# df = df[(df["mean_shared_capacity"] > 0) & (df["mean_degree"] > 0)]
df["log_mean_degree"] = log_transform(df["mean_degree"])
df["log_lifetime"] = log_transform(df["lifetime"])
df["log_mean_shared_capacity"] = log_transform(df["mean_shared_capacity"])

f_data = pd.merge(df, c_data, on=["country"], how="left").drop(["node", "city"], axis=1)
f_data.to_csv(os.path.join(results_dir, "data.csv"), index=True)
