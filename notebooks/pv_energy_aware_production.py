# %%
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import open_mastr
import pandas as pd
import pandera as pa
import requests
import seaborn as sns
from adjustText import adjust_text
from matplotlib import pyplot as plt
from shapely import Point

raw_mastr_file = "mastr_raw_solar.csv"

# %% [markdown]
# # Energy Aware Production
# Download all the data from mastr and use it as parameter estimates

m = open_mastr.Mastr()
m.download()
m.to_csv()

# %% [markdown]
# Load and number of columns (minimizes compute time later on)

base_mastr_path = Path(m.output_dir)
csv_path = base_mastr_path / "data" / "dataversion-2025-02-03" / "bnetza_mastr_solar_raw.csv"

data = pd.read_csv(csv_path)

data[
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

# %% [markdown]
# ## Filter for industrial data
# Allow only rooftop and facade installations, only in industrial settings
# Map and extract orientation, tilt and kwP

map_mastr_orientation_to_degrees_azimuth = {
    "Nord": 180,
    "Nord-Ost": -135,
    "Nord-West": 135,
    "Ost": -90,
    # TODO
    # 'Ost-West',
    "Süd": 0,
    "Süd-Ost": -45,
    "Süd-West": 45,
    "West": 90,
}

map_mastr_orientation_to_pvoutput_orientation = {
    "Nord": "N",
    "Nord-Ost": "NE",
    "Nord-West": "NW",
    "Ost": "E",
    "Ost-West": "EW",
    "Süd": "S",
    "Süd-Ost": "SE",
    "Süd-West": "SW",
    "West": "W",
}

map_pvoutput_to_degrees_azimuth = {
    "N": 180,
    "NE": -135,
    "NW": 135,
    "E": -90,
    # Will be left out for now
    # 'Ost-West',
    "S": 0,
    "SE": -45,
    "SW": 45,
    "W": 90,
}


def filter_mastr(mastr_solar_path: Path, target_path: Path) -> pd.DataFrame:
    # filters mastr data
    # - Must be a rooftop or facade installation
    # - kwP must be over 0 and below the 95% quantile
    # - Must have a valid orientation and inclination
    mastr = pd.read_csv(mastr_solar_path)

    mastr = mastr[mastr["Lage"] == "Bauliche Anlagen (Hausdach, Gebäude und Fassade)"]

    # remove not useful categories:'Nachgeführt', 'Fassadenintegriert', None
    mastr = mastr[
        mastr["HauptausrichtungNeigungswinkel"].isin(["20 - 40 Grad", "< 20 Grad", "40 - 60 Grad", "> 60 Grad"])
    ]
    mastr = mastr[
        mastr["Hauptausrichtung"].isin(
            [
                "Nord",
                "Nord-Ost",
                "Nord-West",
                "Ost",
                "Süd",
                "Süd-Ost",
                "Süd-West",
                "West",
            ]
        )
    ]
    mastr = mastr[
        mastr["Nutzungsbereich"].isin(
            [
                "Industrie"
                # "Haushalt"
                # , 'Landwirtschaft',
                # 'Gewerbe, Handel und Dienstleistungen', nan, 'Sonstige',
                # 'Industrie', 'Öffentliches Gebäude']
            ]
        )
    ]

    # project only necessary columns
    mastr = mastr[["HauptausrichtungNeigungswinkel", "Bruttoleistung", "Hauptausrichtung"]]

    upper_quantile = mastr["Bruttoleistung"].quantile(0.99)
    lower_quantile = mastr["Bruttoleistung"].quantile(0.01)
    mastr = mastr[mastr["Bruttoleistung"] > lower_quantile]
    mastr = mastr[mastr["Bruttoleistung"] < upper_quantile]

    mastr = mastr.dropna()

    # projections and mappings
    mastr["Hauptausrichtung"] = mastr["Hauptausrichtung"].map(lambda x: map_mastr_orientation_to_degrees_azimuth[x])
    mastr.rename(
        columns={
            "Hauptausrichtung": "orientation",
            "HauptausrichtungNeigungswinkel": "coarse_array_tilt_degrees",
            "Bruttoleistung": "kwP",
        },
        inplace=True,
    )

    mastr.to_parquet(target_path)

    return target_path


# %%
file_name = filter_mastr(raw_mastr_file, "industrial_mastr_solar.parquet")
industial_data = pd.read_parquet(file_name)

# %%


def draw_distribution(data: pd.DataFrame):
    data = data.sort_values(by="coarse_array_tilt_degrees")

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plotting the distribution of coarse_array_tilt_degrees
    sns.histplot(data["coarse_array_tilt_degrees"], kde=False, ax=axes[0], color="skyblue", edgecolor="black")
    axes[0].set_title("Distribution of Coarse Array Tilt Degrees")
    axes[0].set_xlabel("Coarse Array Tilt Degrees")
    axes[0].set_ylabel("Frequency")

    # Plotting the distribution of kwP
    sns.histplot(data["kwP"], kde=False, ax=axes[1], color="skyblue", edgecolor="black")
    axes[1].set_title("Distribution of kwP")
    axes[1].set_xlabel("kwP")
    axes[1].set_ylabel("Frequency")

    # Plotting the distribution of orientation
    sns.countplot(x="orientation", data=data, ax=axes[2], color="skyblue", edgecolor="black")
    axes[2].set_title("Distribution of Orientation")
    axes[2].set_xlabel("Orientation")
    axes[2].set_ylabel("Count")

    plt.tight_layout()
    plt.show()


draw_distribution(industial_data)


# %%

# Data
data = [
    {"area": "Upper Austria", "city": "Linz"},
    {"area": "Lower Austria", "city": "Amstetten"},
    {"area": "Lower Austria", "city": "Stockerau"},
    {"area": "Lower Austria", "city": "St. Pölten"},
    {"area": "Styria", "city": "Graz"},
    {"area": "Styria", "city": "Judenburg"},
    {"area": "Styria", "city": "Leoben"},
    {"area": "Kärnten", "city": "Klagenfurt am Wörthersee"},
    {"area": "Kärnten", "city": "Villach"},
    {"area": "Vorarlberg", "city": "Bregenz"},
    {"area": "Tirol", "city": "Innsbruck"},
    {"area": "Salzburg", "city": "Salzburg"},
    {"area": "Burgenland", "city": "Eisenstadt"},
    {"area": "Burgenland", "city": "Oberwart"},
    {"area": "Wien", "city": "Wien"},
]


# Function to get coordinates
def get_coordinates(city, area):
    query = f"{city}, {area}, Austria"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results:
            return results[0]["lat"], results[0]["lon"]
        else:
            print(f"No results found for {query}")
    else:
        print(f"Error: {response.status_code} for {query}")
    return None, None


# Get coordinates for each city
for entry in data:
    lat, lng = get_coordinates(entry["city"], entry["area"])
    entry["latitude"] = lat
    entry["longitude"] = lng
    time.sleep(2)  # Increase delay to avoid overwhelming the server

# Create DataFrame
industrial_cities = pd.DataFrame(data)
print(industrial_cities)


# %%
def plot_coordinates_on_map(df):
    # Load a more detailed map of Austria
    austria = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    austria = austria[austria.name == "Austria"]

    # Create a GeoDataFrame with the coordinates
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)

    # Plot the map
    fig, ax = plt.subplots(figsize=(10, 10))
    austria.plot(ax=ax, color="lightgrey", edgecolor="grey")
    gdf.plot(ax=ax, color="blue", markersize=20)

    # Add labels
    texts = []
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["city"]):
        texts.append(ax.text(x, y, label, fontsize=7, ha="right"))

    # Adjust text to avoid overlap
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color="black"))

    # Remove x and y axis
    ax.set_axis_off()

    # Set title
    plt.title("Industrial Centers in Austria", fontsize=15)

    plt.show()


plot_coordinates_on_map(industrial_cities)

# %% [markdown]
# ## Generating default parameters for each city
# - Use the most common orientation and tilt for each city
# - Use the average kwP for each city


def generate_default_parameters(industrial_parameters: pd.DataFrame) -> dict:
    return {
        "orientation": industrial_parameters["orientation"].value_counts().idxmax(),
        "coarse_array_tilt_degrees": industrial_parameters["coarse_array_tilt_degrees"].value_counts().idxmax(),
        "kwP": int(industrial_parameters["kwP"].mean()),
    }


default_params = generate_default_parameters(industial_data)

print(default_params)

# %% [markdown]
# We assume the tilt is around 10 degrees (no further information is available for the industrial setting) and use 1 kwP (can be upscaled later).
default_params["coarse_array_tilt_degrees"] = 10
default_params["kwP"] = 1

print(default_params)

# %%
hourly_uri = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"


def query_pvgis(config_entry: dict) -> dict | tuple[None, int]:
    # ensure all params are strings
    params = {k: str(v) for k, v in config_entry.items()}

    response = requests.get(hourly_uri, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise requests.HTTPError(f"Request failed with status code {response.status_code}. Reason {response.content}")


@dataclass
class ConfigurationEntry:
    lat: float
    lon: float
    peakpower: float
    angle: float
    aspect: float
    loss: float = 14.0
    outputformat: str = "json"
    mounting: str = "building"
    startyear: int = 2005
    endyear: int = 2020
    usehorizon: int = 1
    pvcalculation: int = 1
    fixed: int = 1  # we work only with fixed modules
    # we work only with crystalline silicon modules, they make up the majority and no data is available for other types
    pvtechchoice: str = "crystSi"


def build_config(locations: dict, params: dict):
    return ConfigurationEntry(
        lat=locations["latitude"],
        lon=locations["longitude"],
        peakpower=params["kwP"],
        angle=params["coarse_array_tilt_degrees"],
        aspect=params["orientation"],
    )


# %%
class NormalizedPVGISSchema(pa.SchemaModel):
    ds: pd.Timestamp = pa.Field()
    power: float = pa.Field(ge=0)  # Assuming power should be >= 0
    global_irradiance: float = pa.Field(ge=0)  # Assuming global irradiance should be >= 0
    sun_height: float = pa.Field()
    temperature_at_2_m: float = pa.Field()
    wind_speed_at_10_m: float = pa.Field()
    is_reconstructed: int = pa.Field(ge=0, le=1)  # Assuming binary values 0 or 1

    class Config:
        strict = True  # Ensure DataFrame only contains the columns defined in the schema


map_pvgis_raw_to_normalized = {
    "time": NormalizedPVGISSchema.ds,
    "P": NormalizedPVGISSchema.power,  # "System output" in watts
    # "Global irradiance on the inclined plane (plane of the array)" in W/m2
    "G(i)": NormalizedPVGISSchema.global_irradiance,
    "H_sun": NormalizedPVGISSchema.sun_height,  # "Sun height" in degrees
    "T2m": NormalizedPVGISSchema.temperature_at_2_m,  # "2-m air temperature" in degrees Celsius
    "WS10m": NormalizedPVGISSchema.wind_speed_at_10_m,  # "10-m total wind speed" in m/s
    "Int": NormalizedPVGISSchema.is_reconstructed,  # "1 means solar radiation values are reconstructed"
}
# %%

base_path = Path("pvgis_data")
base_path.mkdir(exist_ok=True, parents=True)

pvgis_configs = []
for index, meta in industrial_cities.iterrows():
    config = build_config(meta, default_params)
    pvgis_configs.append((meta["city"], asdict(config)))


pvgis_final = []
for city, config in pvgis_configs:
    raw_data = query_pvgis(config)
    # normalize dataframe to standard structure
    data = pd.json_normalize(raw_data["outputs"]["hourly"])
    data = data.rename(columns=map_pvgis_raw_to_normalized).assign(
        ds=lambda df: pd.to_datetime(df["ds"], format="%Y%m%d:%H%M")
    )

    # normalize the city name (replace Umlauts, replace spaces with _, remove dots)
    city = city.replace(" ", "_").replace(".", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    data.to_csv(base_path / f"{city}.csv")
    pvgis_final.append({"city": city, **config})


# %%
# Custom encoder function
def custom_encoder(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return str(obj)


# save the metadata for each one
with open(base_path / "metadata.json", "w") as f:
    json.dump(pvgis_final, f, default=custom_encoder, indent=2)


# %%
# Plotting the power data
city = "Wien"
base_path = Path("pvgis_data")
base_path = Path("/workspace/data/pv/pvgis_data")
data = pd.read_csv(base_path / f"{city}.csv")

data["ds"] = pd.to_datetime(data["ds"])
data.set_index("ds", inplace=True)
fig, ax = plt.subplots(figsize=(12, 6))
data["power"].head(7 * 24).plot(ax=ax, x="ds", color="skyblue")

# Customizing the plot
ax.set_title(f"PV Power Production Over One Week ({city})", fontsize=16)
ax.set_xlabel("Timestamp", fontsize=14)
ax.set_ylabel("Power (W)", fontsize=14)
ax.grid(True, axis="y")

# Formatting the x-axis to show timestamps more clearly
# ax.xaxis.set_major_formatter(plt.FixedFormatter(data['ds'].head(7 * 24)[0:(7*24):24].dt.strftime('%Y-%m-%d %H:%M')))
plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()


# %%
# Resample the data to daily frequency and aggregate (e.g., sum or mean)
monthly_data = data["power"].resample("M").sum()

# Plotting the aggregated power data as a bar plot
fig, ax = plt.subplots(figsize=(12, 6))
monthly_data.head(12).plot(kind="bar", ax=ax, color="skyblue")

# Customizing the plot
ax.set_title(f"Monthly Power Production ({city})", fontsize=16)
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Power (W)", fontsize=14)
ax.grid(True, axis="y")

# Formatting the x-axis to show dates more clearly
ax.set_xticklabels(monthly_data.head(12).index.strftime("%Y %B"), rotation=45, ha="right")

plt.tight_layout()
plt.show()

# %%
daily_power = data["power"].resample("D").sum()
mean_power = daily_power.mean()
median_power = daily_power.median()

plt.hist(daily_power, bins=15, edgecolor="black", alpha=0.7, color="skyblue")

# add mean and median lines
plt.axvline(mean_power, color="r", linestyle="--", label=f"Mean: {mean_power:.2f}")
plt.axvline(median_power, color="g", linestyle="--", label=f"Median: {median_power:.2f}")

# labels, title, and legend
plt.xlabel("Daily Power Production (W)")
plt.ylabel("Count")
plt.title("Histogram of Daily Power Production (W)")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Show plot
plt.show()
# %%
