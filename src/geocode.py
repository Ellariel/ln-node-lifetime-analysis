import os, sys
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import json
import requests
from swiftshadow import QuickProxy


import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", default=None, type=str)
    parser.add_argument("--proxy", default=None, type=str)
    args = parser.parse_args()
else:
    sys.exit()

base_dir = os.path.dirname(__file__)
if "app" in base_dir:
    base_dir = "./"

data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))


if args.proxy:
    proxy = QuickProxy().as_requests_dict()
else:
    proxy = None

print("key:", args.key)
print("data_dir:", data_dir)
print("proxy:", proxy)

addresses = pd.read_csv(os.path.join(data_dir, "addresses.csv"), dtype=str)
addresses = set(addresses.address)

geojson_file = os.path.join(data_dir, "geojson.json")
if os.path.exists(geojson_file):
    with open(geojson_file, "r") as f:
        geojson = json.load(f)
        print("ready:", len(geojson))
else:
    geojson = {}


def flush(data):
    with open(geojson_file, "w") as f:
        json.dump(data, f)


def get_ip(loc, token=None, proxies=None):
    url = f"https://ipinfo.io/{loc}/json"
    if token:
        url += f"?token={token}"
    r = requests.get(url, proxies=proxies)
    if r.ok:
        print(f"ok: {url}")
        return r.json()
    else:
        print(r.text)


test = get_ip("8.8.8.8", token=args.key, proxies=proxy)
if not test:
    print(test)
    sys.exit(0)

counter = 0
for item in tqdm(addresses):
    if item not in geojson and "UNKNOWN" not in item:
        g = get_ip(item, token=args.key, proxies=proxy)
        if g:
            counter += 1
            geojson[item] = g
            if counter >= 500:
                counter = 0
                flush(geojson)
                if args.proxy:
                    proxy = QuickProxy().as_requests_dict()
    # break
flush(geojson)
