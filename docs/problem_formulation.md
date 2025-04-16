# Problem Description

In a staged flowshop scheduling problem, a set of jobs $ J = \{1, \dots, n\} $ is processed sequentially through multiple stages $ S = \{1, \dots, s\} $, each consisting of parallel machines.

Each job $ j $ has a nominal processing time $ P_{j,s}^{\text{nominal}} $ at unit processing speed. The processing speed $ v_{j,s} \in [v_{\min}, v_{\max}] $ can be adjusted per task, affecting both processing time and energy consumption.

# Formulation

## Parameters

- $ v_{\min}, v_{\max} $ – Lower and upper bounds on processing speed  
- $ P_{j,s}^{\text{nominal}} $ – Nominal processing time of job $ j $ at stage $ s $

## Decision Variables

- $ v_{j,s} $ – Processing speed of job $ j $ at stage $ s $  
- $ P_{j,s} $ – Actual processing time  
- $ E_{j,s} $ – Energy consumption  
- $ C_{j,s} $ – Completion time  

## Processing Time and Energy Model

Processing time is inversely proportional to speed:
$$
P_{j,s} = \frac{P_{j,s}^{\text{nominal}}}{v_{j,s}}
$$

Energy consumption is given by:
$$
E_{j,s} = \alpha v_{j,s}^{\beta} P_{j,s}
$$

Substituting $P_{j,s}$ yields:
$$
E_{j,s} = \alpha v_{j,s}^{\beta - 1} P_{j,s}^{\text{nominal}}
$$

where:

- $ \alpha $ is a scaling factor  
- $ \beta > 0 $; determines how energy scales with speed

For $ \alpha = 1 $:

- $ \beta = 0 $ - Energy decreases with higher speed ($E \propto \frac{1}{v}$)
- $ \beta = 1 $ - Constant energy consumption ($E = P^{\text{nominal}}$), independent of speed
- $ \beta = 2 $ - Energy grows linearly with speed ($E \propto v$)
- $ \beta = 3 $ - Energy increases quadratically with speed ($E \propto v^2$)

For an interactive example see [here](https://www.geogebra.org/classic/cvkz3kq5)

## Objectives

- **Minimize makespan**:
  $$
  C_{\max} = \max_j C_{j,s}
  $$
  where $s$ denotes the final stage

- **Minimize total energy consumption**

- **Balance performance and energy efficiency** by optimizing the speed-energy trade-off

- **Prevent peak grid overload** by bounding instantaneous power

## Coupling Scheduling Load with PV

To integrate photovoltaic (PV) energy availability, we estimate the scheduling power demand and compare it to available PV capacity.

### Definitions

- $ \text{makespan}_\text{best}^{(i)} $ – Best-known makespan for instance $ i $  
- $ P_{j,s}^{\text{nominal}} $ – Nominal processing time  
- $ M_s $ – Set of machines at stage $ s $  

### Total Processing Time

$$
T_{\text{total}}^{(i)} = \sum_{j=1}^n \sum_{k=1}^s P_{j,k}^{\text{nominal}}
$$

### Average Concurrent Machine Usage

$$
\bar{m}^{(i)} = \frac{T_{\text{total}}^{(i)}}{\text{makespan}_\text{best}^{(i)}}
$$

### Estimated Load at Speed $v$

Assuming a uniform processing speed $v$ and it's corresponding amplifier $a$ across all jobs and stages, the average power demand is approximated by:

$$
\text{Load}_v^{(i)} = \bar{m}^{(i)} \cdot a
$$

This linear estimate assumes constant machine utilization and no idle time.

### PV Scaling Factor

Let $ W_p^{\text{PV}} $ denote the peak PV output in watts (e.g., $1000$ W = $1$ kWp). The required PV system size to supply the estimated load is:

$$
\text{Scaling Factor}^{(i)} = \frac{\text{Load}_v^{(i)}}{W_p^{\text{PV}}}
$$

This dimensionless factor indicates how many times larger than a 1 kWp system the PV capacity must be to support execution at speed $v$.

> **Note:** All power values are expressed in watts (W). This model assumes constant power demand.

### Summary of Variables

| Variable | Description |
|---------|-------------|
| $ P_{j,s}^{\text{nominal}} $ | Nominal processing time |
| $ \text{makespan}_\text{best}^{(i)} $ | Best-known makespan |
| $ \bar{m}^{(i)} $ | Average concurrent machine usage |
| $ v $ | Uniform processing speed assumed for load estimation |
| $ W_p^{\text{PV}} $ | Peak PV capacity (W) |
| $ \text{Scaling Factor}^{(i)} $ | Dimensionless PV scaling factor |

### Additional Objectives

- Minimize required PV scaling factor  
- Align execution with PV production profiles, maximizing the PV usage  
- Limit grid dependency by bounding $ \text{Load}_v^{(i)} $

---

### Multi-Objective Consideration

These objectives can be incorporated into a weighted or Pareto-based multi-objective optimization framework to explore trade-offs between makespan, energy efficiency, and renewable energy utilization.
