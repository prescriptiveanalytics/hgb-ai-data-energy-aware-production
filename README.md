# Energy Aware Production Codebase

This README serves as a **TLDR** for detailed documentation look at the docs and the data package in the release page.

TODO: add link to documentation

## Repository Structure

### Notebooks
The repository includes several notebooks for different tasks. These are the main contribution of this project.

- **`0_open_mastr_download.py`**: Handles downloading and preprocessing of PV-related data from the MaStR database. This includes filtering and mapping relevant parameters for energy-aware production.
- **`1_pv_energy_aware_production.py`**: Focuses on analyzing PV energy production data, including mapping coordinates, visualizing distributions, and normalizing PVGIS data.
- **`2_scheduling_instances.py`**: Prepares scheduling problem instances by transforming input data into JSON format and adding speedup and energy consumption parameters for tasks.
- **`3_scheduling_coupling_with_pv.py`**: Couples scheduling load with PV energy production data to analyze the interplay between scheduling and renewable energy availability.

### Package
The package, provides utilities for:

- Accessing the data package (`EnergyAwareSchedulingDataPackage`).
- Defining and validating problem instances (`ProblemInstance`, `Job`, `Task`, etc.).
- Reading and processing best-known makespans and other scheduling-related data.