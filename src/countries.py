import os, sys
import ray
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import networkx as nx
import nx_parallel as nxp
from itertools import batched

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_country_dist(g):
    metrics = {"capacity": {}, "degree": {}, "channel": {}, "node": {}}
    for i in g.nodes:
        n = g.nodes[i]
        if "geojson" in n and "country" in n["geojson"]:
            c = n["geojson"]["country"]
            metrics["capacity"].setdefault(c, 0)
            metrics["degree"].setdefault(c, 0)
            metrics["channel"].setdefault(c, 0)
            metrics["node"].setdefault(c, 0)
            metrics["degree"][c] += g.degree(i)
            metrics["node"][c] += 1
            for e in g.edges(i):
                metrics["channel"][c] += 1
                metrics["capacity"][c] += (
                    float(g.edges[e].get("htlc_maximum_msat", 0)) / 2000
                )  # msat -> sat
    for i in metrics["degree"].keys():
        metrics["degree"][i] = metrics["degree"][i] / metrics["node"][i]
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default=None, type=str)
    parser.add_argument("--results_dir", default=None, type=str)
    parser.add_argument("--num_cpu", default=35, type=int)
    parser.add_argument("--batch_size", default=10, type=int)
    args = parser.parse_args()
else:
    sys.exit()

base_dir = os.path.dirname(__file__)
if "app" in base_dir:
    base_dir = "./"
data_dir = os.path.join(base_dir, "data") if args.data_dir is None else args.data_dir
results_dir = (
    os.path.join(base_dir, "results") if args.results_dir is None else args.results_dir
)
os.makedirs(results_dir, exist_ok=True)
cpu_count = max(1, os.cpu_count() - 2)
num_cpu = min(args.num_cpu, cpu_count)
batch_size = min(args.batch_size, cpu_count)
print("data_dir:", data_dir)
print("results_dir:", results_dir)
print("num_cpu:", num_cpu)
print("batch_size:", batch_size)

print(f"networkx: {nx.__version__}")
print(f"nx_parallel: {nxp.__version__}")
os.environ["NETWORKX_AUTOMATIC_BACKENDS"] = "parallel"
os.environ["RAY_memory_monitor_refresh_ms"] = "500"
# nx.config.backends.parallel.active = True
# nx.config.backends.parallel.n_jobs = num_cpu

ray.init(num_cpus=num_cpu)

results_file = os.path.join(results_dir, "country_dist.csv")


@ray.remote
def proccess_graph(g, seed=13):
    set_seed(seed)
    ug = nx.read_gml(g).to_undirected()
    metrics = pd.DataFrame(get_country_dist(ug))
    metrics["timestamp"] = get_stamp(g)
    metrics["year"] = get_stamp(g)[:4]
    metrics["nodes"] = len(ug.nodes)
    metrics["channels"] = len(ug.edges)
    metrics.reset_index(names="country", inplace=True)
    return metrics


graphs = pd.read_csv(
    os.path.join(results_dir, "geographs.csv"), parse_dates=True, index_col=0
)

if os.path.exists(results_file):
    results = pd.read_csv(results_file, dtype=str)
else:
    results = pd.DataFrame()


timestamps = set(results.timestamp) if "timestamp" in results else set()
for batch in tqdm(
    batched(graphs.fname, batch_size), total=len(graphs.fname) // batch_size
):
    batch = [
        proccess_graph.remote(os.path.join(data_dir, g))
        for g in batch
        if get_stamp(g) not in timestamps
    ]
    if len(batch):
        results = pd.concat([results] + ray.get(batch))
        results.to_csv(results_file, index=False)
