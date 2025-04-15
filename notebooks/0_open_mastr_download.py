# %%

from pathlib import Path

import open_mastr
import pandas as pd

from energy_aware_production.data_package import (
    EnergyAwareSchedulingDataPackage,
    LocalPaths,
)

# %%

dp = EnergyAwareSchedulingDataPackage(LocalPaths.data)

# %% [markdown]
# # Data for Energy Aware Production
# Download all the data from mastr and use it to estimate which PV
# Parameters are used in productin.
# Careful! This will download a lot of data and take a long time. You can use
# the precalculated data later on.

m = open_mastr.Mastr()
m.download()
m.to_csv()

# %% [markdown]
# Load and minimize number of columns (minimizes compute time later on)

base_mastr_path = Path(m.output_dir)
raw_mastr_file = "mastr_raw_solar.csv"
csv_path = base_mastr_path / "data" / "dataversion-2025-02-03" / "bnetza_mastr_solar_raw.csv"

data = pd.read_csv(csv_path)

data[
    # relevant columns
    [
        "Lage",
        "Hauptausrichtung",
        "Einspeisungsart",
        "Einheittyp",
        "Bruttoleistung",
        "Registrierungsdatum",
        "Postleitzahl",
        "Laengengrad",
        "Breitengrad",
        "Nettonennleistung",
        "FernsteuerbarkeitNb",
        "FernsteuerbarkeitDv",
        "FernsteuerbarkeitDr",
        "EinheitlicheAusrichtungUndNeigungswinkel",
        "GemeinsamerWechselrichterMitSpeicher",
        "HauptausrichtungNeigungswinkel",
        "Nutzungsbereich",
    ]
].to_csv(raw_mastr_file)

# %%

data = pd.read_csv(dp.pv_mastr_column_filtered)
data.head()
print(data.shape)
