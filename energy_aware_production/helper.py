from pathlib import Path


def read_makespan_file(filepath: Path):
    best_known_makespans = {}

    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 4:
                key = (parts[0], parts[1], parts[2])
                value = int(parts[3])
                best_known_makespans[key] = value

    return best_known_makespans
