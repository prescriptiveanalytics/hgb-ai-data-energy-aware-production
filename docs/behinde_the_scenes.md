# Behinde the Scenes

### Notebooks
The repository includes several notebooks for different tasks. These are the main contribution of this project.

#### Open MaStr Download (`0_open_mastr_download.py`)

Handles downloading and preprocessing of PV-related data from the MaStR database. This includes filtering and mapping relevant parameters for energy-aware production. The notebook is only available in code form as it takes quite a bit of time to run.

#### Create PV Data Package (`1_pv_energy_aware_production.py`)
Focuses on analyzing PV energy production data, including mapping coordinates, visualizing distributions, and normalizing PVGIS data.

<iframe src="/notebooks/1_pv_energy_aware_production.html" width="100%" height="600px"></iframe>

#### Create Scheduling Data Package (`2_scheduling_instances.py`)
Prepares scheduling problem instances by transforming input data into JSON format and adding speedup and energy consumption parameters for tasks.

<iframe src="/notebooks/2_scheduling_instances.html" width="100%" height="600px"></iframe>

#### Couple Scheduling Instances with PV (`3_scheduling_coupling_with_pv.py`)
Couples scheduling load with PV energy production data to analyze the interplay between scheduling and renewable energy availability.

<iframe src="/notebooks/3_scheduling_coupling_with_pv.html" width="100%" height="600px"></iframe>
