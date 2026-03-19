import os, sys
import argparse
import random
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_dt(s):
    s = os.path.split(s)[1].split(".")[0]
    return s


def set_seed(seed=13):
    random.seed(seed)
    np.random.seed(seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default=None, type=str)
    parser.add_argument("--shapes_file", default="shapes.csv", type=str)
    args = parser.parse_args()
else:
    sys.exit()

base_dir = os.path.dirname(__file__)
if "app" in base_dir:
    base_dir = "./"

data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))

print("data_dir:", data_dir)
print(os.path.join(data_dir, "nodes.csv"))

nodes_df = pd.read_csv(
    os.path.join(data_dir, "nodes.csv"),
    index_col=0,
    parse_dates=True,
    sep="#",
    quotechar="+",
    engine="python",
)
nodes_df = (
    nodes_df.reset_index()
    .groupby("node")
    .agg(
        {
            "shared_capacity": "mean",
            "timestamp": lambda x: (x.max() - x.min()).days,
            "degree": "mean",
        }
    )
    .rename(
        columns={
            "timestamp": "lifetime",
            "shared_capacity": "mean_shared_capacity",
            "degree": "mean_degree",
        }
    )
    .reset_index()
)

addresses = os.path.join(data_dir, "addresses.csv")
geojson = os.path.join(data_dir, "geojson.json")

if os.path.exists(geojson):
    with open(geojson, "r") as f:
        geojson = json.load(f)
else:
    geojson = {}

if os.path.exists(addresses):
    addresses = pd.read_csv(addresses, dtype=str)
    addresses.set_index("node", inplace=True)
else:
    addresses = pd.DataFrame()

if len(addresses) < 1 or len(geojson) < 1:
    print("There is some issues with data files..")
    sys.exit()


geo_data = []
geo_cols = ["city", "region", "country", "latitude", "longitude"]

for n in tqdm(nodes_df["node"]):
    try:
        geo = geojson[addresses.loc[n]["address"]]
        for col in geo_cols:
            if col not in geo:
                geo[col] = np.nan
        loc = geo.get("loc", np.nan)
        if isinstance(loc, str) and "," in loc:
            lat, lon = loc.split(",")
            geo["latitude"] = float(lat)
            geo["longitude"] = float(lon)
        geo_data.append(
            {
                "city": geo["city"],
                "region": geo["region"],
                "country": geo["country"],
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
            }
        )
    except:  # noqa: E722
        geo_data.append(
            {
                "city": np.nan,
                "region": np.nan,
                "country": np.nan,
                "latitude": np.nan,
                "longitude": np.nan,
            }
        )

geo_df = pd.DataFrame(geo_data)
final_df = pd.concat([nodes_df, geo_df], axis=1)
print(f"Number of items: {len(final_df)}")
final_df.to_csv(os.path.join(data_dir, "geo_nodes.csv"), index=False)
