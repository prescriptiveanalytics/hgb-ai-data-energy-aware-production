from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field


@dataclass
class LocalPaths:
    root: Path = Path(__file__).parent.parent
    data: Path = root / "data"


class SchedulingDataPackage:
    def __init__(self, root: Path):
        self.root = root
        self.scheduling = root / "scheduling"

        self.raw_input = self.scheduling / "raw_input"
        self.scheduling_instances = self.raw_input / "instances"
        self.scheduling_bounds = self.raw_input / "best_makespans.txt"

        self.schema_json = self.scheduling / "schema.json"
        self.json_instances = self.scheduling / "instances"
        self.parameters_json = self.json_instances / "parameters.json"


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


class Machine(BaseModel):
    machine_id: int = Field(alias="MachineId")
    stage_number: int = Field(alias="StageNumber")

    class Config:
        populate_by_name = True


class Stage(BaseModel):
    machines: List[Machine] = Field(alias="Machines")

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
    pv_scaling_factor: float = Field(alias="PvScalingFactor", default=None)
    best_known_makespan: int = Field(alias="BestKnownMakespan")
    best_known_energy: int = Field(alias="BestKnownEnergy")
    stage_list: List[Stage] = Field(alias="StageList")
    job_list: List[Job] = Field(alias="JobList")

    class Config:
        populate_by_name = True
