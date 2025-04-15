# Energy Aware Production Codebase

This repository contains the code and tools for generating and analyzing problem instances of an **Energy Aware Scheduling Problem**. The project focuses on optimizing scheduling in staged flowshop environments, where tasks can be sped up at the cost of increased energy consumption.

TODO: Docs
TODO: Data
This README serves as a **TLDR** for detailed documentation look at the docs and the data package in the release page.

## Repository Structure

### Notebooks
The repository includes several Jupyter notebooks for different aspects of the project:

- **`0_open_mastr_download.py`**: Handles downloading and preprocessing of PV-related data from the MaStR database. This includes filtering and mapping relevant parameters for energy-aware production.
- **`1_pv_energy_aware_production.py`**: Focuses on analyzing PV energy production data, including mapping coordinates, visualizing distributions, and normalizing PVGIS data.
- **`2_scheduling_instances.py`**: Prepares scheduling problem instances by transforming input data into JSON format and adding speedup and energy consumption parameters for tasks.
- **`3_scheduling_coupling_with_pv.py`**: Couples scheduling load with PV energy production data to analyze the interplay between scheduling and renewable energy availability.

### Package
The repository includes a Python package, `energy_aware_production`, which provides utilities for:
- Managing data packages (`EnergyAwareSchedulingDataPackage`).
- Defining and validating problem instances (`ProblemInstance`, `Job`, `Task`, etc.).
- Reading and processing best-known makespans and other scheduling-related data.

### Data
The data used in this project is documented in its own README files located in the respective data directories. These include:

- **`data/scheduling/README.md`**: Describes the scheduling problem, its formulation, and the structure of the provided data.
- **`data/pv/README.md`** (if applicable): Documents PV-related data, including sources and preprocessing steps.

You can download the data from the [releases page](https://github.com/prescriptiveanalytics/hgb-ai-data-energy-aware-production/releases)

## Problem Description
The **Energy Aware Scheduling Problem** involves scheduling multiple jobs across multiple stages in a flowshop environment. Each job has a nominal processing time but can be processed at different speeds, impacting both processing time and energy consumption. The main goal is to optimize scheduling while balancing energy efficiency and makespan. The data package also provides PV data from multiple industrial sites in europe, which can be used to define more interesting szenarios. 