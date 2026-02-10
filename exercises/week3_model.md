# Week 3: MILP Formulation & Implementation

## Overview

This week, you will implement the optimization model that solves the line planning problem. You'll add constraints to a Mixed Integer Linear Program (MILP) that determines which bus lines to operate and at what frequencies.

By the end of this week, you will:
- Understand how binary and continuous variables model line planning decisions
- Implement capacity constraints that link line frequencies to available capacity
- Implement flow conservation constraints that route passengers through the network
- Successfully solve the Winterthur line planning problem

**Time Estimate:** 12 hours per team (6 hours per student)

## Learning Objectives

By the end of Week 3, you should be able to:
1. Explain how binary variables model discrete line frequency choices
2. Explain how continuous variables model passenger flows through the network
3. Implement capacity constraints linking line decisions to available capacity
4. Implement flow conservation constraints
5. Understand the objective function trade-off between passenger cost and vehicle cost
6. Use PuLP library to formulate and solve linear programming models

## Background: The Line Planning Optimization Problem

The line planning problem seeks to minimize total system cost (passenger travel time + vehicle operating cost) by deciding:
1. **Which lines to operate** (binary decision: yes/no for each line)
2. **At what frequency** (discrete choice: e.g., every 15, 30, or 60 minutes)

The optimization must satisfy:
- **Flow conservation**: All passengers must reach their destinations
- **Capacity constraints**: Buses cannot exceed their capacity
- **Fleet constraints**: Limited number of vehicles available

This line planning problem is solved for a single period. That means the solution to the problem measures the total number of passengers on each node and link of the passenger flow network for an entire period (e.g. the number of people using a bus line between two stations over all buses of that line in that period). We implicitly assume an equal distribution of passengers and demand over the period.

### Configurable Parameters

The optimization can be configured through parameters in [parameters.py](../src/openbus_light/plan/parameters.py) that affect which lines are selected and at what frequencies:

**Permitted Frequencies**: Define the discrete frequency choices available for each line (as a divisor of the planning period i.e. how many services are operated per period). Finer granularity gives more flexibility but increases problem complexity. The model selects at most one frequency per line.

**Cost Parameters**: The objective function balances passenger generalized travel time (weighted by value-of-time coefficients for waiting, walking, in-vehicle time, and access/egress) against vehicle operating costs.

**Network Parameters**: Walking speed and maximum walking distance determine which walking connections exist in the network for transfers or direct walks.

**Constraints**: Demand scaling controls the percentage of daily demand to consider for planning a single period. The maximum number of vehicles creates a hard budget constraint that forces trade-offs between coverage and frequency.

By adjusting these parameters, you can explore questions like: What happens if we value passenger time twice as much? How many vehicles do we need for 50% vs 100% of demand? If passengers walk 500m instead of 300m, how many buses can we save?

### Decision Variables

The model uses two types of decision variables:

1. **Binary variables**: `line_configuration[line, frequency]`
   - One binary variable for each (line, frequency) pair
   - Value of 1 means: operate this line at this frequency
   - Value of 0 means: don't operate this line at this frequency
   - Constraint ensures at most one frequency per line

2. **Continuous variables**: `passenger_flow[origin, link]`
   - One variable for each (origin station, network link) pair
   - Represents: how many passengers from this origin use this link
   - Non-negative values (can't have negative passenger flow)

## Task 1: Implement Capacity Constraints

Capacity constraints ensure that passenger flow on each link does not exceed the available vehicle capacity. The available capacity depends on which line frequency is selected.

**Location**: [src/openbus_light/plan/problem.py](../src/openbus_light/plan/problem.py)

**Function**: `_add_capacity_constraints()`

You need to implement capacity constraints for RIDE and BOARD links. 

Consider:
- What is the available line capacity over one period?
- How can you calculate the total flow over this link?
- How do you consider only the available capacity of the selected frequency for that line?
- There is a slight difference between RIDE and BOARD links. What is it?

## Task 2: Implement Flow Conservation Constraints

Flow conservation constraints ensure that passengers flow through the network correctly:
- At origin stations: passengers enter the network
- At destination stations: passengers exit the network
- At intermediate stations: flow in equals flow out

**Location**: [src/openbus_light/plan/problem.py](../src/openbus_light/plan/problem.py)

**Function**: `_add_flow_conservation_constraints()`

### Mathematical Formulation

Each origin-destination pair creates a flow that needs to be routed through the network. The flow enters the network at the **ACCESS** node of the origin station and exits the network at the **EGRESS** node of the destination station. For each node it holds:
```
sum(flow_out) - sum(flow_in) = flow_balance
```

Where `flow_balance` is:
- **At ACCESS node of origin**: demand entering the network from this origin
- **At EGRESS node of destination**: demand to destination from that origin
- **At all other nodes**: 0 (flow just passes through)

**This is the hardest constraint to implement!** Take your time, draw diagrams, and test with small examples.

## Task 3: Implement test functions

To verify your understanding of the optimization model, you will implement test functions in the test file.

**Location**: [test/test_problem.py](../test/test_problem.py)

**Test Functions**:
1. `test_number_of_capacity_constraints_correct()` - Verify that the correct number of capacity constraints are added to the model
2. `test_flow_balance_at_origin()` - Verify flow conservation at origin nodes (flow entering network equals demand)
3. `test_flow_balance_at_destination()` - Verify flow conservation at destination nodes (flow exiting network equals demand)
4. `test_flow_balance_at_intermediate()` - Verify flow conservation at intermediate nodes (inflow equals outflow)

Each test function includes a docstrings to guide your implementation. For calculating expected values, you should not hard-code the values you expect but calculate them based on the input scenario and network structure.

## Task 4: Write Technical Report

Write a **2-page technical report** explaining the MILP formulation.

**Required Content:**

### 1. Variable Definitions

- Explain what `line_configuration[line, frequency]` represents
- Explain what `passenger_flow[origin, link]` represents
- Explain why there is one flow from each origin rather than considering all flow from all origins at once
- Explain why we track flow per origin rather than per OD pair

### 2. Constraints

**Capacity Constraints:**
- Mathematical formulation
- Explain how they link line decisions to passenger flows
- Why does capacity depend on frequency selection?
- Why do we need capacity constraints on RIDE and BOARD links both?

**Flow Conservation:**
- Mathematical formulation with a small example
- Explain the sign convention

### 3. Objective Function
- Passenger cost component (generalized travel time)
- Vehicle operating cost component
- Trade-off between service quality and cost

### 4. Limitations
- Describe the limitations of the line planning model formulation and suggest possible improvements


**Format**: PDF, maximum 2 pages

## Testing Your Implementation

After implementing the constraints, verify everything works:

```bash
# Run all Week 3 tests
pytest test/test_problem.py -v
pytest test/test_line_planning.py -v

# Try solving the full Winterthur scenario
python line_planning.py --demand_scaling=0.1 --experiment_id=test_week3 --use_current_frequencies=True
```

If the model solves successfully and produces results in `results/test_week3/`, you're done!

**Note**: Passing tests don't guarantee correctness - ensure your logic is sound and matches the expected behavior.

## Deliverables

Submit the following files:

- [ ] [src/openbus_light/plan/problem.py](../src/openbus_light/plan/problem.py) - Implemented `_add_capacity_constraints()` and `_add_flow_conservation_constraints()`
- [ ] [test/test_problem.py](../test/test_problem.py) - Implemented missing tests and all tests pass
- [ ] `exercises/week3_report.pdf` - 2-page technical report explaining the MILP formulation
- [ ] Model successfully solves the Winterthur scenario

## Grading Rubric (25% of Final Grade)

**Capacity Constraints**
- Correctness
- Tests implemented correctly and all pass
- Clean, readable code following Python conventions

**Flow Conservation**
- Correctness
- Tests implemented correctly and all pass
- Clean, readable code following Python conventions

**Technical Report**
- Clear explanation of variables and their purpose 
- Correct mathematical formulation of constraints
- Clear description of trade-offs in objective
- Demonstrates understanding by considering limitations of the model

## Getting Help

**Office Hours:** Thursday afternoon, participate by choosing a time slot on Moodle

**Discussion Forum on Moodle:** Post your questions so everyone can profit from the answer!

### Debugging Tips
- Look at the `.lp` file that gets written if the model is infeasible
- Use the test file to understand and debug expected behavior, it can actually help to first write the test before doing the implementation
- Draw small examples by hand
