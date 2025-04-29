# Problem Description

In a staged flowshop scheduling problem, a set of jobs $ J = \{1, \dots, n\} $ is processed sequentially through multiple stages $ S = \{1, \dots, s\} $, each consisting of parallel machines.

Each job $ j $, contains $s$ number of tasks $t_{j,s}$, which have a nominal processing time $ P_{j,s}^{\text{nominal}} $ at unit processing speed. The processing speed $ v_{j,s} \in [v_{\min}, v_{\max}] $ can be adjusted per task, affecting both processing time and energy consumption.

# Formulation

The following variables are from the literature, they are part of a benchmarking suit. The suit comes with multiple instances (problems) in different sizes.

- $ I = \{1, \dots, i\} $ - Number of instances (with varying sizes)

Each instance has a few defined variables:

- $ S = \{1, \dots, s\} $ - Number of stages in a given instance
- $ J = \{1, \dots, n\} $ - Number of jobs in a given instance
- $ \text{makespan}_\text{best}^{(i)} $ - Best known makespan for instance $i$.
- $ P_{j,s}^{\text{nominal}} $ – Nominal processing time of task $t$ (of job $ j $) at stage $ s $, each job has only one task in each stage

## Extended Modelling Energy Consumption - Processing Time and Energy Model

### Parameters for Generating the Problem

- $ v_{\min}, v_{\max} $ – Lower and upper bounds on processing speed  

### The Energy Model

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

- $ \alpha $ is a scaling factor where $ \alpha > 0 $  
- $ \beta \geq 0 $; determines how energy scales with speed

For $ \alpha = 1 $:

- $ \beta = 0 $ - Energy decreases with higher speed ($E \propto \frac{1}{v}$)
- $ \beta = 1 $ - Constant energy consumption ($E = P^{\text{nominal}}$), independent of speed
- $ \beta = 2 $ - Energy grows linearly with speed ($E \propto v$)
- $ \beta = 3 $ - Energy increases quadratically with speed ($E \propto v^2$)

For an interactive example see [here](https://www.geogebra.org/classic/cvkz3kq5)

## Coupling Scheduling Load with PV

To integrate photovoltaic (PV) energy availability, we estimate the scheduling power demand and compare it to available PV capacity.

### Definitions

- $ M_s $ – Set of machines at stage $ s $  
- $ a $ - The amplifications which is calculated by the extended energy consumption.

### Total Processing Time

$$
T_{\text{total}}^{(i)} = \sum_{j=1}^n \sum_{k=1}^s P_{j,k}^{\text{nominal}}
$$

### Average Concurrent Machine Usage

$$
\bar{m}^{(i)} = \frac{T_{\text{total}}^{(i)}}{\text{makespan}_\text{best}^{(i)}}
$$

### Estimated Typical Load at Speed $v$

Assuming a uniform processing speed $v$ and it's corresponding amplifier $a$ across all jobs and stages, the average power demand is approximated by:

$$
\text{Typical Load}_v^{(i)} = \bar{m}^{(i)} \cdot a
$$

This linear estimate assumes constant machine utilization and no idle time. Additionally, we expect the factor $ a $ returns the typical load in Watts.

### PV Scaling Factor

Let $ W_p^{\text{PV}} $ denote the peak PV output in watts (e.g., $1000$ W = $1$ kWp). The required PV system size to supply the estimated load is:

$$
\text{PV Scaling Factor}^{(i)} = \frac{\text{Load}_v^{(i)}}{W_p^{\text{PV}}}
$$

This dimensionless factor indicates how many times larger than a 1 kWp system the PV capacity must be to support execution at speed $v$.

> **Note:** All power values are expressed in watts (W). This model assumes constant power demand.

## Output

- A solution candidate for the problem - a fixed schedule. For each task the schedule should contain when a tasks starts, how long it takes (processing time) and how much energy it took while running. Additionally, it makes sense to include time of completion and the used speedup.


## Derived Values from the Output

These can be calculated based on the given output. They serve as a basis for calculating objectives and comparing solutions, they are directly calculated from the solution candidate:

- $ P_{j,s} $ – Actual processing time for each task
- $ E_{j,s} $ – Energy consumption for each task
- $ C_{j,s} $ – Completion time of each task
- $ v_{j,s} $ – Processing speed of job $ j $ at stage $ s $  
- $ E_{t} $ - Consumed energy over time

## Objectives

- **Minimize makespan**:
  $$
  C_{\max} = \max_j C_{j,s}
  $$
  where $s$ denotes the final stage

- **Minimize total energy consumption**:
  $$
  E_{total} = \sum_{j=1}^{J} \sum_{s=1}^{S} E_{j,s}
  $$

- **Balance performance and energy efficiency** 

- **Prevent peak grid overload** by bounding instantaneous power:
  $$
  E(t) \leq E_{\text{max}} \quad \forall \, t \in [0, T]
  $$

- **Align execution with PV production profiles, maximizing the PV usage**  

---

### Multi-Objective Consideration

These objectives can be incorporated into a weighted or Pareto-based multi-objective optimization framework to explore trade-offs between makespan, energy efficiency, and renewable energy utilization.
