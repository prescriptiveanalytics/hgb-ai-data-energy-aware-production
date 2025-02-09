from dataclasses import dataclass
from pathlib import Path


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