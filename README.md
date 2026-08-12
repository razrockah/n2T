## WORK IN PROGRESS
# n2T — neutron to tritium

A lithium enrichment optimization analysis project for fusion breeder blankets, built on [OpenMC](https://openmc.org).

n2T sweeps the Li-6 enrichment fraction of a blanket model and will find the configuration that maximizes the tritium breeding ratio (TBR). Python drives the OpenMC neutronics, Julia (`analysis/`) handles the tally data analysis and plotting.


