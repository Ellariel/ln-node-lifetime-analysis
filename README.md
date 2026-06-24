# Scripts and Data for the Paper “Shared Channel Capacity and Node Lifetime: An Empirical Study of the Lightning Network”

## Quick Start

If your goal is to reproduce the analytical results and figures, you do **not** need to run the full data preparation pipeline.

A cleaned and aggregated dataset of node characteristics is already provided in:

```
results/data.csv
```

You can reproduce the analysis and figures directly by running:

```
analysis.ipynb
```

from the root directory.

## Full Data Pipeline (Optional)

The snapshot data preparation pipeline is documented in a separate repository:
[[github]](https://github.com/ellariel/ln-data-preparation).

The complete pipeline is included for reproducibility purposes. To rebuild the dataset from raw data, execute the scripts in the order shown below.

All input data, intermediate outputs, and final results should be stored in the `data/` directory during execution.

| Stage               | Scripts                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1. Data acquisition | Manual download, see also [[github]](https://github.com/ellariel/ln-data-preparation).                                                                                                  |
| 2. Geo-processing   | `geocode.py` (retrieves geolocation data via API) <br> `geonodes.py` (assigns geodata to nodes across snapshots) |
| 3. Data cleaning    | `nodes.py` (filters and aggregates node-level information)                                                       |

## Notes

* The full pipeline is only necessary if you want to regenerate the dataset from scratch.
* API usage in the geo-processing stage may require credentials or rate limiting considerations.
* Ensure that all scripts are executed sequentially to avoid missing dependencies between steps.

#### Citation

```latex
Danila Valko and Jorge Marx Gómez (2026). Shared channel capacity and node lifetime: An empirical study of the lightning network. arXiv. https://doi.org/10.48550/arXiv.2606.20566
```

```latex
@misc{ValkoMarxGomez2026,
title={Shared channel capacity and node lifetime: An empirical study of the lightning network}, 
author={Danila Valko and Jorge {Marx G\'omez}},
year={2026},
publisher={arXiv},
howpublished={arXiv},
eprint={2606.20566},
doi={10.48550/arXiv.2606.20566},
archivePrefix={arXiv},
primaryClass={cs.NI},
}
```