# %%
import json
from pathlib import Path
from typing import Dict, Generator, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from energy_aware_production_data.data_package import (
    EnergyAwareSchedulingDataPackage,
    Job,
    LocalPaths,
    Machine,
    ProblemInstance,
    Stage,
    Task,
)
from energy_aware_production_data.helper import read_makespan_file

# %%
# # Scheduling Instances
# We prepare the scheduling instances by transforming the input data into a JSON format and
# adding information about the speedup and increased energy consumption for each task.

dp = EnergyAwareSchedulingDataPackage(LocalPaths.data)


# %% [markdown]
# First we read the best known makespans from a file
# Lookup table for best known makespan
BEST_KNOWN_MAKESPANS = read_makespan_file(dp.scheduling_bounds)


# %%
def load_text_files_from_directory(base_dir: Path, pattern="*.txt") -> Generator[tuple[str, str], None, None]:
    """
    Loads text files from a given directory that match the specified pattern.

    :param base_dir: The base directory containing the files.
    :param pattern: The filename pattern (default: "*.txt").
    :return: A generator yielding (filename, file_content) tuples.
    """
    file_paths = base_dir.glob(pattern)

    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            yield file_path, file.read()


# %%
def calculate_amplifiers(v_range: List[float], alpha: float, beta: float) -> Dict[float, float]:
    amplifiers = {}
    for v in v_range:
        amplifiers[v] = round(v**beta * alpha, 2)
    return amplifiers


def calculate_speedup_for_task(
    amplifiers: dict[int, float],
    processing_time: int,
    *,
    precision_energy: int = 3,
    precision_time: int = 3,
) -> Dict[int, float]:
    """
    Calculate the speedup and energy cost for a given processing time and energy amplifiers.
    """

    speedup = {}
    for time_divisor, energy_increase_factor in amplifiers.items():
        # pt = processing time
        pt_speedup = round(processing_time / time_divisor, precision_time)
        total_energy_cost = processing_time * energy_increase_factor
        energy_per_pt = round(total_energy_cost / pt_speedup, precision_energy)

        # map speedup processing time to energy costs per minute
        speedup[int(pt_speedup)] = int(energy_per_pt)
    return speedup


def transform_input_to_json(
    input_str: str,
    instance_id: str,
    *,
    v_min: float = 1,
    v_max: float = 2.0,
    v_step: float = 0.1,
    alpha: float = 1.0,
    beta: float = 2.0,
    input_energy_coverage: float = 0.8,
    average_input_energy: float | None = None,
) -> str:
    lines = input_str.strip().split("\n")

    # Read Number of Jobs and Number of Stages
    num_jobs, num_stages = map(int, lines[0].split())

    # Read number of machines per stage
    machines_per_stage = list(map(int, lines[1].split()))

    # Read processing times for jobs
    # processing_times = [list(map(int, line.split())) for line in lines[2:]]
    processing_times = np.array([list(map(int, line.split())) for line in lines[2:]]).T

    # Define speed range using numpy for better precision
    v_range = np.round(np.arange(v_min, v_max + v_step, v_step), 2).tolist()

    # Retrieve known makespan from lookup table
    best_known_makespan = BEST_KNOWN_MAKESPANS.get(tuple(instance_id.split("_")), -1)
    if best_known_makespan == -1:
        raise ValueError(f"Best known makespan not found for instance {instance_id}")

    # Calculate alpha based on the provided energy source. It should cover
    # the energy consumption of about 80% of the makespan.
    if average_input_energy is not None:
        alpha = (best_known_makespan * input_energy_coverage) / average_input_energy

    best_known_energy = best_known_makespan * alpha

    # Compute velocity amplifiers
    amplifiers = calculate_amplifiers(v_range, alpha, beta)

    # Construct the JSON structure
    machine_id = 0
    stage_list = []
    for stage_number, num_machines in enumerate(machines_per_stage):
        machines = [Machine(machine_id=machine_id + i, stage_number=stage_number) for i in range(num_machines)]
        stage_list.append(Stage(machines=machines))
        machine_id += num_machines

    task_id = 0
    job_list = []
    for job_id, job_times in enumerate(processing_times):
        tasks = []
        for stage, time in enumerate(job_times):
            tasks.append(
                Task(
                    id=task_id, stage=stage, processing_time=time, speed_up=calculate_speedup_for_task(amplifiers, time)
                )
            )
            task_id += 1
        job_list.append(Job(id=job_id, tasks=tasks))

    return ProblemInstance(
        number_of_jobs=num_jobs,
        number_of_stages=num_stages,
        instance=instance_id.split("_")[-1],
        best_known_makespan=best_known_makespan,
        best_known_energy=best_known_energy,
        stage_list=stage_list,
        job_list=job_list,
        amplifiers=amplifiers,
        alpha=alpha,
        beta=beta,
    )


# %%
city = "Wien"
base_path = Path("/workspace/data/pv/pvgis_data")
data = pd.read_csv(base_path / f"{city}.csv")
data["ds"] = pd.to_datetime(data["ds"])
data.set_index("ds", inplace=True)

daily_power = data["power"].resample("D").sum()
mean_power = daily_power.mean()
median_power = daily_power.median()

# %% [markdown]
# Lastly we define necessary parameters
parameters = dict(
    v_min=1,
    v_max=2.0,
    v_step=0.1,
    alpha=1000,
    beta=2.0,
    # average_input_energy=median_power,
)
# %%
# Example usage
schema = None
for index, (filename, content) in enumerate(load_text_files_from_directory(dp.scheduling_instances), start=1):
    instance_id = filename.name.replace("instancia_", "").replace(".txt", "")
    instance = transform_input_to_json(content, instance_id, **parameters)

    if schema is None:
        schema = instance.model_json_schema()

    stringified = json.dumps(instance.model_dump(by_alias=True))
    # save to file
    target_path = (dp.scheduling_json_instances / instance_id).with_suffix(".json")
    with open(target_path, "w") as file:
        file.write(stringified)

# save the schema to a file
with open(dp.scheduling_schema_json, "w") as file:
    json.dump(schema, file, indent=4)

with open(dp.scheduling_parameters_json, "w+") as file:
    json.dump(parameters, file, indent=4)

# %%
# extract values
values = list(BEST_KNOWN_MAKESPANS.values())

# calculate mean and median
mean_value = np.mean(values)
median_value = np.median(values)

plt.figure(figsize=(10, 6))
plt.plot(values, marker="o", linestyle="-", color="b", label="Makespan")
plt.xlabel("Instance Index")
plt.ylabel("Makespan")
plt.title("Best Known Makespans")
plt.legend()
plt.grid(True)
plt.show()
# %%
# group data by the task size
grouped_data = {}
for key, value in BEST_KNOWN_MAKESPANS.items():
    group = int(key[0])
    if group not in grouped_data:
        grouped_data[group] = []
    grouped_data[group].append(value)

# calculate the average makespan for each group
average_makespans = {group: np.mean(values) for group, values in grouped_data.items()}

sorted_groups = sorted(average_makespans.keys())
sorted_averages = [average_makespans[group] for group in sorted_groups]

# Plot
plt.figure(figsize=(12, 6))
plt.bar(sorted_groups, sorted_averages, color="skyblue")
plt.xlabel("Number of Stages")
plt.ylabel("Average Makespan")
plt.title("Average Makespan by Number of Stages")
plt.xticks(sorted_groups)
plt.grid(axis="y")
plt.show()


# %%
