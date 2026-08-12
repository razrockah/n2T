# n2T — neutron to tritium

A lithium enrichment optimization tool for fusion breeder blankets, built on [OpenMC](https://openmc.org).

n2T sweeps the Li-6 enrichment fraction of a parametric blanket model and finds the value that maximizes the tritium breeding ratio (TBR). Python drives the OpenMC neutronics; Julia (`analysis/`) handles the tally data analysis and plotting.

**Work in progress** — currently just the parametric blanket geometry, imported from [model_benchmark_zoo](https://github.com/fusion-energy/model_benchmark_zoo).
