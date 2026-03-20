import os, sys, glob
import argparse
import random
import json
import networkx as nx
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

files = pd.read_csv(os.path.join(data_dir, args.shapes_file), dtype={"datetime": str})

results = [
    get_dt(f)
    for f in glob.glob(os.path.join(data_dir, "*.json"))
    if os.path.isfile(f) and "geojson" not in f
]


for f, dt in tqdm(
    files[["fname", "datetime"]].itertuples(index=False), total=len(files)
):
    f = os.path.join(data_dir, f)
    if os.path.exists(f) and dt not in results:
        nodes = {}
        g = nx.read_gml(f)
        for n in g.nodes:
            shared_capacity = np.sum(
                [d["capacity_sat"] / 2 for u, v, d in g.edges(n, data=True)]
            )
            nodes.setdefault(n, g.nodes[n])
            nodes[n].update(
                {"timestamp": dt, "node": n, "shared_capacity": shared_capacity}
            )
        if len(nodes) > 0:
            with open(os.path.join(data_dir, f"{dt}.json"), "w") as fio:
                json.dump(nodes, fio, indent=4)
    # break

results = []
for f in tqdm(glob.glob(os.path.join(data_dir, "*.json"))):
    with open(f, "r") as fio:
        for i, d in json.load(fio).items():
            d["degree"] = d.pop("out_degree", 0) + d.pop("in_degree", 0)
            [
                d.pop(k, None)
                for k in [
                    "features",
                    "rgb_color",
                    # "out_degree",
                    # "in_degree",
                ]
            ]
            results.append(d)
    # break
df = pd.DataFrame(results)
print(f"Number of items: {len(df)}")  # 2239066
df.to_csv(
    os.path.join(data_dir, "nodes.csv"),
    sep=";",
    index=False,
)
