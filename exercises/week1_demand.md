# Week 1: Data Exploration & Understanding the Domain

## Overview

This week, you will explore the Winterthur public transport network and understand how passenger demand is captured and associated to bus stations.

By the end of this week, you will:
- Have the code up and running and be able to load the demand and network data 
- Understand how the origin destination matrix is associated to the bus network (i.e. the `DemandMatrix`).
- Implement two analysis functions to compute demand statistics
- Create visualizations showing network structure and demand patterns
- Hand-in a short two-page report

**Time Estimate:** 12 hours per team (6 hours per student)

## Learning Objectives

By the end of Week 1, you should be able to:
1. Explain how the origin-destination data is mapped to the public transport demand and its the influence on the line planning model
2. Create and interpret visualizations of demand patterns
3. Implement simple data validation and unit tests for domain models

## Setup

See [docs/setup.md](../docs/setup.md) for the setup instructions.

## Task 1: Implement Tests and Data Validation

This task helps you understand the data structures by implementing validation methods and unit tests. You'll work with two files:
- [src/openbus_light/model/scenario.py](../src/openbus_light/model/scenario.py): Implement the consistency check methods
- [test/test_demand.py](../test/test_demand.py): Implement 2 unit tests

### Part A: Scenario Consistency Checks (`scenario.py`)

A `Scenario` contains `stations`, `bus_lines`, and `demand_matrix`. All stations referenced in lines and demand must exist in the station list, and all stations must be served by at least one line. The main method to implement is **`check_consistency()`**. The methods **`_check_station_and_lines_consistency()`** and **`_check_station_and_demand_consistency()`** are helper methods that
verify the station/line consistency and the consistency of the demand matrix with respect to stations and lines. **`check_consistency()`** must raise `ValueError` with an appropriate message on failure.

See the method signatures and docstrings in [scenario.py](../src/openbus_light/model/scenario.py) for details.

### Part B: DemandMatrix Unit Tests (`test_demand.py`)

Implement two tests to verify `DemandMatrix` behavior:

1. **`test_incoming_equals_outgoing_demand(baseline_scenario)`**:
   - Verify total incoming demand equals total outgoing demand (conservation of flow)
   - Use `pytest.approx()` for floating-point comparisons

2. **`test_zero_association_radius_no_demand()`**:
   - Load scenario with `demand_association_radius=Meter(0)`
   - What are the consequences of this parameter on the Scenario? Verify this in the test.

See the function signatures and docstrings in [test_demand.py](../test/test_demand.py) for details.

### Part C: Propose Two Additional Tests

Implement two additional tests for `DemandMatrix` in [test_demand.py](../test/test_demand.py).
Explain in the docstring why each test is meaningful.

## Task 2: Create Visualizations

Implement at least **2 visualizations** in [exercises/week1_plot.py](week1_plot.py) to explore the network and demand patterns. These visualizations should support your report's explanation of network structure and demand distribution.

**You have freedom to choose:**
- What to visualize (network map, demand flows, station loads, demand radius effects, etc.)
- How to visualize (matplotlib, plotly, simple charts, etc.)
- What insights to highlight

**Reference:** See [src/openbus_light/plot/](../src/openbus_light/plot/) for inspiration, but implement your own functions.

## Task 3: Write Report

Write a **2 to 4-page report** giving an overview of the Winterthur transport network and the demand in the network, including how the demand is processed for consideration in the line planning model.

**Important:** This report forms the foundation of your course documentation. Each week, you will extend this same report with new sections, building a cohesive story that connects all aspects of the line planning problem. By the end of the course, you will submit one complete report with a unified narrative covering demand analysis, network modeling, optimization formulation, and scenario analysis.

### Network and Demand Overview

**What to include:**

1. **Network Structure**: 
   - Describe the basics of the transport network in Winterthur (topology, important nodes).
   - Description of bus lines and frequencies
   - Briefly describe the network topology (linear, hub-and-spoke, grid?)

2. **Demand Patterns**
   - Describe the demand distribution across the network 
   - Describe how the origin-destination data is associated with stations
      - how does the `demand_association_radius` influence the result?
      - what is a realistic value?
      - what are the consequences of this approach for line planning?
   
3. **Visualizations**
   - Use the visualizations you created in week1_plot.py to help with the explanation
   - Visualizations should show network structure and demand patterns or help explain the mapping from origin-destination data to stations

**Tips:**
- Use tables to present statistics clearly
- Label all figures with captions

## Testing Your Implementation

After implementing your methods and tests, verify everything works:

```bash
# Test your scenario consistency implementation
pytest test/test_scenario.py -v

# Run your DemandMatrix tests
pytest test/test_demand.py -v
```

**Note**: Passing tests don't guarantee correctness - ensure your logic is sound.

## Deliverables

Submit the following files:

- [ ] [src/openbus_light/model/scenario.py](../src/openbus_light/model/scenario.py) - Implemented consistency check method
- [ ] [test/test_demand.py](../test/test_demand.py) - Implemented 2 unit tests and 2 additional tests
- [ ] [exercises/week1_plot.py](week1_plot.py) - Implemented min. 2 visualization functions
- [ ] `exercises/week1_report.pdf` - 2 to 4-page report with analysis and visualizations
- [ ] All tests pass: `test_scenario.py` and `test_demand.py`

## Grading Rubric (25% of Final Grade)

**Code Quality**
- Consistency check and tests implemented correctly
- Code passes all unit tests
- Clean, readable code following Python conventions

**Visualizations**
- At least 2 visualizations included in report
- Plots are clear and properly labeled
- Visualizations appropriately support the report

**Analysis & Report**
- Clear description of network structure and demand
- Demonstrates understanding of the data and how demand is processed
- Report follows scientific style
- Clear use of tables and figures

## Getting Help

**Office Hours:** Thursday afternoon, participate by choosing a time slot on Moodle

**Discussion Forum on Moodle:** Post your questions so everyone can profit from the answer!
