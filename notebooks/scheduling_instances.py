# %%
import json
from pathlib import Path
from typing import Any, Dict, Generator, List

from matplotlib import pyplot as plt
import numpy as np
from pydantic import BaseModel, Field

from energy_aware_production.data_package import SchedulingDataPackage, LocalPaths

# %%
# # Scheduling Instances
# We prepare the scheduling instances by transforming the input data into a JSON format and
# adding information about the speedup and increased energy consumption for each task.

dp = SchedulingDataPackage(LocalPaths.data)

# %% [markdown]
# First we read the best known makespans from a file
def read_makespan_file(filepath: Path):
    best_known_makespans = {}
    
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 4:
                key = (parts[0], parts[1], parts[2])
                value = int(parts[3])
                best_known_makespans[key] = value
    
    return best_known_makespans


# Lookup table for best known makespan
BEST_KNOWN_MAKESPANS = read_makespan_file(dp.scheduling_bounds)

# %% [markdown]
# Then we define the structure of the json. 

class Machine(BaseModel):
    machine_id: int = Field(alias="MachineId")
    stage_number: int = Field(alias="StageNumber")

    class Config:
        populate_by_name = True

class Stage(BaseModel):
    machines: List[Machine] = Field(alias="Machines")

    class Config:
        populate_by_name = True

class Task(BaseModel):
    id: int = Field(alias="Id")
    stage: int = Field(alias="Stage")
    processing_time: int = Field(alias="ProcessingTime")
    # this keys will be strings (json enforces keys to be strings)
    speed_up: Dict[Any, float] = Field(alias="SpeedUp")

    class Config:
        populate_by_name = True

class Job(BaseModel):
    id: int = Field(alias="Id")
    tasks: List[Task] = Field(alias="Tasks")

    class Config:
        populate_by_name = True

class ProblemInstance(BaseModel):
    number_of_jobs: int = Field(alias="NumberOfJobs")
    number_of_stages: int = Field(alias="NumberOfStages")
    instance: int = Field(alias="Instance")
    # this keys will be strings (json enforces keys to be strings)
    amplifiers: dict[Any, float] = Field(alias="Amplifiers")
    alpha: float = Field(alias="Alpha")
    beta: float = Field(alias="Beta")
    best_known_makespan: int = Field(alias="BestKnownMakespan")
    best_known_energy: int = Field(alias="BestKnownEnergy")
    stage_list: List[Stage] = Field(alias="StageList")
    job_list: List[Job] = Field(alias="JobList")

    class Config:
        populate_by_name = True

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
        amplifiers[v] = round(v ** beta * alpha, 2)
    return amplifiers

def calculate_speedup(
        amplifiers: dict[int, float], 
        processing_time: int,
        *,
        precision_enenrgy: int = 2
) -> Dict[int, float]:
    return {
        int(round((processing_time / k), 0)): round(processing_time * v, precision_enenrgy) 
        for k, v in amplifiers.items()
    }

def transform_input_to_json(
    input_str: str, instance_id: str, 
    *, 
    v_min: float = 1, v_max: float = 2.0, v_step: float = 0.1, 
    alpha: float = 1.0, beta: float = 2.0
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
    best_known_makespan = BEST_KNOWN_MAKESPANS.get(tuple(instance_id.split('_')), -1)
    if best_known_makespan == -1:
        raise ValueError(f"Best known makespan not found for instance {instance_id}")
    
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
            tasks.append(Task(
                id=task_id, stage=stage, processing_time=time, speed_up=calculate_speedup(amplifiers, time)
            ))
            task_id += 1
        job_list.append(Job(id=job_id, tasks=tasks))
    
    return ProblemInstance(
        number_of_jobs=num_jobs,
        number_of_stages=num_stages,
        instance=instance_id.split('_')[-1],
        best_known_makespan=best_known_makespan,
        best_known_energy=best_known_energy,
        stage_list=stage_list,
        job_list=job_list,
        amplifiers=amplifiers,
        alpha=alpha,
        beta=beta
    )

# %% [markdown]
# Lastly we define necessary parameters
parameters = dict(
    v_min=1, v_max= 2.0, v_step=0.1, alpha=10, beta= 2.0,
)
# %%
# Example usage
schema = None
for index, (filename, content) in enumerate(load_text_files_from_directory(Path('/workspace/data/scheduling/raw_input/instances')), start=1):
    instance_id = filename.name.replace('instancia_', '').replace('.txt', '')
    instance = transform_input_to_json(content, instance_id, **parameters)

    if schema is None:
        schema = instance.model_json_schema()

    stringified = json.dumps(instance.model_dump(by_alias=True))
    # save to file
    target_path = (dp.json_instances / instance_id).with_suffix('.json')
    with open(target_path, "w") as file:
        file.write(stringified)

# save the schema to a file
with open(dp.schema_json, "w") as file:
    json.dump(schema, file, indent=4)

with open(dp.parameters_json, "w+") as file:
    json.dump(parameters, file, indent=4)

# %%
# extract values
values = list(BEST_KNOWN_MAKESPANS.values())

# calculate mean and median
mean_value = np.mean(values)
median_value = np.median(values)

plt.figure(figsize=(10, 6))
plt.plot(values, marker='o', linestyle='-', color='b', label='Makespan')
plt.xlabel('Instance Index')
plt.ylabel('Makespan')
plt.title('Best Known Makespans')
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
plt.bar(sorted_groups, sorted_averages, color='skyblue')
plt.xlabel('Number of Stages')
plt.ylabel('Average Makespan')
plt.title('Average Makespan by Number of Stages')
plt.xticks(sorted_groups)
plt.grid(axis='y')
plt.show()



# %%
