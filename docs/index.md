# Home

The **Energy Aware Scheduling Problem** involves scheduling multiple jobs across multiple stages in a flowshop environment. Each job has a nominal processing time but can be processed at different speeds, impacting both processing time and energy consumption. The main goal is to generate an optimal schedule while balancing energy efficiency and makespan. Additionally, the problem allows to for more objectives like renewable utilization and power shaping. The data package also provides PV data from multiple industrial sites in europe, which can be used to define more interesting scenarios. 

The problem data is based on tested data from academic literature[^1].

## Getting Started
Project is split up into multiple sections: 

- **[Usage](usage.md)**: How to use the data for your own optimization algorithm.
- **[Problem Instance Structure](problem_formulation.md)**: Describes the scheduling problem, its formulation, and the structure of the provided data.
- **[Data Package Structure](data_package.md)**: Describes the structure of the data package.

You can download the data from the [releases page](https://github.com/prescriptiveanalytics/hgb-ai-data-energy-aware-production/releases).

## Main Contributions

- **Advanced Scheduling Benchmark**:
A comprehensive set of scheduling instances is introduced, where tasks can optionally be accelerated based on configurable speedup parameters. An interactive [GeoGebra explainer](https://www.geogebra.org/classic/cvkz3kq5) is included to visually demonstrate how speedup decisions affect scheduling behavior.

- **Grounded in Literature & Systematically Generated**:
The scheduling problem is based on established formulations from academic literature. Parameterized instance generation enables controlled experimentation across a wide range of problem sizes and configurations.

- **Robust and Portable Data Format**:
A schema.json is provided to support fast, type-safe parsing and validation of instance data across multiple programming environments, improving usability and integration.

- **Transparent Data for Reproducibility**:
All raw instance data is made available to ensure full transparency and reproducibility of experimental results.

- **Realistic Industrial Energy Context**:
Example output data reflects real-world industrial energy use, using locations in Austria selected based on economic relevance (e.g., federal capitals or entries in the Industrie Landkarte).

- **Empirical Parameterization from [MaStr](https://www.marktstammdatenregister.de/MaStR)**:
Real-world solar PV system characteristics (e.g., orientation, tilt, and capacity) are derived from the German MaStr project, specifically filtered for the industrial sector.

- **Reliable Environmental and Economic Inputs**:
Solar generation potential is based on PVGIS data using typical configurations. Electricity pricing reflects real 2024 market values, sourced from APG, enabling accurate cost modeling.


[^1]: Fernandez-Viagas, V., & Framinan, J. M. (2020). Design of a testbed for hybrid flow shop scheduling with identical machines. Computers & Industrial Engineering, 141(106288), 106288. doi:10.1016/j.cie.2020.106288