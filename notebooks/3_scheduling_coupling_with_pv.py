# %%

from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from energy_aware_production.data_package import LocalPaths, SchedulingDataPackage, ProblemInstance
from energy_aware_production.helper import read_makespan_file

# %%
dp = SchedulingDataPackage(LocalPaths.data)
print(list(dp.scheduling_instances.glob('*')))

# %%

best_known_makespans = read_makespan_file(dp.scheduling_bounds)

typical_amplifier = '1.8'

stats = []
for instance in dp.json_instances.glob('*.json'):
    if instance.name.endswith('parameters.json'):
        continue

    with open(instance, 'r') as f:
        data = f.read()
        try:
            pi = ProblemInstance.model_validate_json(data)
        except Exception as e:
            print(f"Error reading {instance}: {e}")
            continue

        instance_identifier = (
            (
                str(pi.number_of_jobs), 
                str(pi.number_of_stages), 
                str(pi.instance),
            )
        )
        best_known_makespan = best_known_makespans.get(instance_identifier, None)

        if best_known_makespan is None:
            raise ValueError(f"Instance {pi.instance} not found in best known makespans.")

        total_processing_time = 0
        for job in pi.job_list:
            for task in job.tasks:
                total_processing_time += task.processing_time

        number_of_total_machines = sum([len(stage.machines) for stage in pi.stage_list])
        average_running_machines = total_processing_time / best_known_makespan

        avg_energy_per_speedup = {}
        for k,v in pi.amplifiers.items():
            avg_energy_per_speedup[k] = v * average_running_machines

        stats.append({
            "instance": pi.instance,
            "number_of_jobs": pi.number_of_jobs,
            "number_of_stages": pi.number_of_stages,
            "number_of_available_machines": number_of_total_machines,
            "typical_load": avg_energy_per_speedup[typical_amplifier],
            "average_running_machines": average_running_machines,
            "best_known_makespan": best_known_makespan,
            "total_processing_time": total_processing_time,
        })

stats = pd.DataFrame(stats)
# %%

assert (stats['average_running_machines'] > stats['number_of_available_machines']).sum() == 0

# %%

stats['required_pv_kwP'] = stats['typical_load'] / 1000.

# %%

# Plot the bar chart
plt.figure(figsize=(12, 6))
plt.bar(stats['number_of_jobs'], stats['required_pv_kwP'], alpha=0.7, color='blue')

# Add labels and title
plt.xlabel('Instance Size (Stages * Jobs)', fontsize=12)
plt.ylabel('Typical Load', fontsize=12)
plt.title('Typical Load vs Instance Size', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.show()

# %%
plt.figure(figsize=(10, 6))
sns.histplot(
    stats['required_pv_kwP'],
    bins=16,
    color='skyblue',
    edgecolor='black'
)

# Add lines for mean and median
mean_val = stats['required_pv_kwP'].mean()
median_val = stats['required_pv_kwP'].median()
plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f} kWp')
plt.axvline(median_val, color='green', linestyle='-.', linewidth=2, label=f'Median: {median_val:.2f} kWp')

# Labels and style
plt.title('Distribution of Required PV System Sizes', fontsize=14)
plt.xlabel('Required PV Size (kWp)', fontsize=12)
plt.ylabel('Number of Instances', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# %%
