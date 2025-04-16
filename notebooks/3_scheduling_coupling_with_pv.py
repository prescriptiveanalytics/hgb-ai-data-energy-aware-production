# %%
import json

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from energy_aware_production_data.data_package import (
    EnergyAwareSchedulingDataPackage,
    LocalPaths,
    ProblemInstance,
)
from energy_aware_production_data.helper import read_makespan_file

# %%
dp = EnergyAwareSchedulingDataPackage(LocalPaths.data)

# %% [markdown]
# # Helper Functions


def read_instance(path_to_instance: str) -> ProblemInstance:
    with open(path_to_instance, "r") as f:
        data = f.read()
        try:
            return ProblemInstance.model_validate_json(data)
        except Exception as e:
            raise RuntimeError(f"Error parsing Instance ({path_to_instance}) JSON to class") from e


best_known_makespans = read_makespan_file(dp.scheduling_bounds)

# %% [markdown]
# # Coupling scheduling load with PV

typical_amplifier = "1.8"
# assumed peak energy production of the PV system
assumed_Wp_of_pv = 1000

stats = []
for instance_path in dp.scheduling_json_instances.glob("*.json"):
    if instance_path.name.endswith("parameters.json"):
        continue

    pi = read_instance(instance_path)
    instance_identifier = (
        str(pi.number_of_jobs),
        str(pi.number_of_stages),
        str(pi.instance),
    )
    best_known_makespan = best_known_makespans.get(instance_identifier, None)

    if best_known_makespan is None:
        raise ValueError(f"Instance {pi.instance} not found in best known makespans.")

    # calculate total work load
    total_processing_time = 0
    for job in pi.job_list:
        for task in job.tasks:
            total_processing_time += task.processing_time

    # calculate average running machines per instance
    number_of_total_machines = sum([len(stage.machines) for stage in pi.stage_list])
    average_running_machines = total_processing_time / best_known_makespan

    # calculate average load based on the chosen amplifier
    avg_energy_per_speedup = {}
    for k, v in pi.amplifiers.items():
        avg_energy_per_speedup[k] = v * average_running_machines

    # calculate scaling factor for PV system
    pv_scaling_factor = avg_energy_per_speedup[typical_amplifier] / assumed_Wp_of_pv
    pi.pv_scaling_factor = round(pv_scaling_factor, 3)

    # save the updated model instance as json
    stats.append(
        {
            "instance": pi.instance,
            "number_of_jobs": pi.number_of_jobs,
            "number_of_stages": pi.number_of_stages,
            "total_instance_size": pi.number_of_jobs * pi.number_of_stages,
            "number_of_available_machines": number_of_total_machines,
            "average_running_machines": average_running_machines,
            "typical_load": avg_energy_per_speedup[typical_amplifier],
            "assumed_Wp_of_pv": assumed_Wp_of_pv,
            "pv_scaling_factor": pv_scaling_factor,
            "best_known_makespan": best_known_makespan,
            "best_known_energy": pi.best_known_energy,
            "alpha": pi.alpha,
            "beta": pi.beta,
            "typical_amplifier": typical_amplifier,
            "total_processing_time": total_processing_time,
        }
    )

    # update the instance with the new scaling factor
    stringified = json.dumps(pi.model_dump(by_alias=True))
    with open(instance_path, "w") as file:
        file.write(stringified)

stats = pd.DataFrame(stats)
stats.to_csv(dp.scheduling_stats_csv)

# %%
# update parameters
with open(dp.scheduling_parameters_json, "r") as file:
    data = json.load(file)

data["typical_amplifier"] = typical_amplifier

with open(dp.scheduling_parameters_json, "w") as file:
    json.dump(data, file, indent=4)

# %% [markdown]
# ## Checks
# Ensure that the number of available machines is greater than the estimated average running machines
assert (stats["average_running_machines"] > stats["number_of_available_machines"]).sum() == 0

# %%

# Plot the bar chart
plt.figure(figsize=(12, 6))
plt.bar(stats["number_of_jobs"], stats["pv_scaling_factor"], alpha=0.7, color="blue")

# Add labels and title
plt.xlabel("Instance Size (Jobs)", fontsize=12)
plt.ylabel("PV Scaling Factor[kWp]", fontsize=12)
plt.title("Number of Jobs vs. PV Scaling Factor", fontsize=14)
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Show the plot
plt.show()

# %%
# ## Visualization
# In the following step we visualize how much we need to scale up a PV system (which is close to 1 kwP)
plt.figure(figsize=(10, 6))
sns.histplot(stats["pv_scaling_factor"], bins=16, color="skyblue", edgecolor="black")

# Add lines for mean and median
mean_val = stats["pv_scaling_factor"].mean()
median_val = stats["pv_scaling_factor"].median()
plt.axvline(mean_val, color="red", linestyle="--", linewidth=2, label=f"Mean: {mean_val:.2f} kWp")
plt.axvline(median_val, color="green", linestyle="-.", linewidth=2, label=f"Median: {median_val:.2f} kWp")

# Labels and style
plt.title("Distribution of Required PV System Sizes", fontsize=14)
plt.xlabel("Required PV Size (kWp)", fontsize=12)
plt.ylabel("Number of Instances", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# %%
