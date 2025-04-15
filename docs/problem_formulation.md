# Problem Description

In a staged flowshop scheduling problem, multiple jobs $ J = \{1, ..., n\} $ are processed through multiple stages $ S = \{1, ..., s\} $, where each stage has a set of parallel machines.

Each job $ j $ has a nominal processing time $ P_{j,s}^{\text{nominal}} $ at unit speed. However, jobs can be processed at different speeds $ v_{j,s} $, which impacts both the processing time and the energy consumption.

# Formulation

## Known Variables

- $ v_{max} $, $ v_{min} $ – Minimal and maximal speedup which can be applied to a task  
- $ P^{\text{nominal}}_{j,s} $ – Processing time of job $ j $ at stage $ s $ without any speedup.

## Decision Variables

- $ v_{j,s} $ – Processing speed of job $ j $ at stage $ s $ (continuous variable).
- $ P_{j,s} $ – Actual processing time of job $ j $ at stage $ s $.
- $ E_{j,s} $ – Energy consumption of job $ j $ at stage $ s $.
- $ C_{j,s} $ – Completion time of job $ j $ at stage $ s $.

## Speedup and Energy Consumption

Each task can be sped up or slowed down using a speedup between $ v_{\min} $ and $ v_{\max} $. The processing time scales inversely with speed:

$$
P_{j,s} = \frac{P_{j,s}^{\text{nominal}}}{v_{j,s}}
$$

The total energy consumption for a job $ j $ at stage $ s $ is given by:

$$
E_{j,s} = \alpha v_{j,s}^{\beta} P_{j,s}
$$

where:

- $ E_{j,s} $ is the energy consumption,  
- $ v_{j,s} $ is the processing speed,  
- $ P_{j,s} $ is the actual processing time,  
- $ \alpha $ is a scaling factor showing how much energy per process time is necessary,  
- $ \beta $ determines how energy scales with speed ($ \beta \geq 0 $).

Assuming $ \alpha = 1 $, this equation shows that:

- If $ \beta = 2 $, energy scales quadratically with speed.
- If $ \beta > 2 $, increasing speed causes non-linear energy growth.
- If $ 1 < \beta < 2 $, energy grows slower than quadratically but still increases.
- If $ \beta = 1 $, energy grows linearly with speed.
- If $ \beta = 0 $, energy cost equals processing time regardless of speed.

## Objectives

The main objectives are:

- **Minimize makespan** ($ C_{\max} $), the total time required to process all jobs.
- **Minimize total energy consumption** ($ P_{\max} $).
- **Balance the trade-off** between speed and power consumption.
- **Avoid reaching peak grid load** ($ P_{\max} $).
