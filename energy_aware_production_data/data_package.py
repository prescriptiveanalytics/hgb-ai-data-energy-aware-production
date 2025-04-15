from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field


@dataclass
class LocalPaths:
    """
    The following is wrapper class for locally developing the data package. It acts as configuration where `data` is stored by default.
    """
    root: Path = Path(__file__).parent.parent
    data: Path = root / "data"


class EnergyAwareSchedulingDataPackage:
    """
    This represents the structure of the data package. It is used to access the 
    data files and directories. Generally, the data is split into two parts: PV and scheduling
    """
    def __init__(self, root: Path):
        self.root = root

        # pv related fields
        self.pv = root / "pv"
        self.pv_figures = self.pv / "figures"
        self.pv_meta = self.pv / "meta"
        self.pv_industrial_cities = self.pv_meta / "industrial_cities.csv"
        self.pv_mastr_column_filtered = self.pv_meta / "mastr_column_filtered.csv"
        self.pv_industrial_parameter_distribution = self.pv_meta / "industrial_parameter_distribution.csv"
        self.pv_mastr_industrial_solar = self.pv_meta / "mastr_industrial_solar.csv"

        self.pv_pvgis_data = self.pv / "pvgis_data"
        self.pv_energy_prices = self.pv / "energy_prices_2024.csv"

        # scheduling
        self.scheduling = root / "scheduling"
        self.scheduling_raw_input = self.scheduling / "raw_input"
        self.scheduling_instances = self.scheduling_raw_input / "instances"
        self.scheduling_bounds = self.scheduling_raw_input / "best_makespans.txt"
        self.scheduling_json_instances = self.scheduling / "instances"

        # schema for generating class files for different programming languages
        self.scheduling_schema_json = self.scheduling / "schema.json"

        # parameters for creating instances
        self.scheduling_parameters_json = self.scheduling_json_instances / "parameters.json"


class Task(BaseModel):
    """
    The Attributes of a single Task. The speed up is a dictionary where the keys represent processing times
     and their associated energy costs.
    """
    id: int = Field(alias="Id")
    stage: int = Field(alias="Stage")
    processing_time: int = Field(alias="ProcessingTime")
    # this keys will be strings (json enforces keys to be strings)
    speed_up: Dict[Any, float] = Field(alias="SpeedUp")

    class Config:
        populate_by_name = True


class Job(BaseModel):
    """
    The Attributes of a single Job. The tasks are represented as a list of Task objects.
    """
    id: int = Field(alias="Id")
    tasks: List[Task] = Field(alias="Tasks")

    class Config:
        populate_by_name = True


class Machine(BaseModel):
    """
    A machine is represented by its ID and the stage it belongs to. 
    The stage number is used to identify the machine's position in the production process.
    """
    machine_id: int = Field(alias="MachineId")
    stage_number: int = Field(alias="StageNumber")

    class Config:
        populate_by_name = True


class Stage(BaseModel):
    """
    A stage is represented by its ID and the list of machines that belong to it.
    For the flow shop problem it is assumed a stage with an id smaller than another one
    must be passed before getting to the next stage.
    """
    machines: List[Machine] = Field(alias="Machines")

    class Config:
        populate_by_name = True


class ProblemInstance(BaseModel):
    """
    The whole problem instance. It contains meta data from the original
    scheduling problem (number_of_jobs, number_of_stages, best_known_makespan, instance id) and the list of jobs and stages.
    Additionally, it contains the amplifiers, alpha and beta values, which are used to 
    generate the energy consumption of the tasks. Finally, it contains a pv scaling factor 
    which tells you how many kWp of PV are expected to used for this instance.
    """
    number_of_jobs: int = Field(alias="NumberOfJobs")
    number_of_stages: int = Field(alias="NumberOfStages")
    instance: int = Field(alias="Instance")
    # this keys will be strings (json enforces keys to be strings)
    amplifiers: dict[Any, float] = Field(alias="Amplifiers")
    alpha: float = Field(alias="Alpha")
    beta: float = Field(alias="Beta")
    pv_scaling_factor: float = Field(alias="PvScalingFactor", default=None)
    best_known_makespan: int = Field(alias="BestKnownMakespan")
    best_known_energy: int = Field(alias="BestKnownEnergy")
    stage_list: List[Stage] = Field(alias="StageList")
    job_list: List[Job] = Field(alias="JobList")

    class Config:
        populate_by_name = True
