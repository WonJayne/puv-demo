# Week 2: Network Construction & Graph Representation

## Overview

This week, you will learn how to construct the passenger flow network that represents how passengers move through the public transport system. This network is essential for the optimization algorithm you'll implement in Week 3.

By the end of this week, you will:
- Understand the 4-node structure (ACCESS, EGRESS, TRANSFER, SERVICE) used to model passenger journeys
- Implement functions to calculate walkable distances between stations
- Create the network links that connect nodes representing different passenger activities
- Visualize and debug network topology

**Time Estimate:** 12 hours per team (6 hours per student)

## Learning Objectives

By the end of Week 2, you should be able to:
1. Explain why the passenger flow network has 4 node types per station (ACCESS, EGRESS, TRANSFER, SERVICE) and how they enable modeling of different passenger activities
2. Implement the graph structure creation functions by considering how to link the nodes together
3. Visualize and debug network topology to verify correct graph construction and explain the passenger flow network

## Background: Understanding the Passenger Flow Network

The passenger flow network models how passengers move through the public transport system, similar to water flowing through a network of pipes. Just as water takes the path of least resistance, passengers will take the path that minimizes their total travel cost (generalized travel time).

**How the network models passenger flow**:
- **Nodes** represent a location (i.e. a particular station) and a state in which passengers exists
- **Links** represent activities passengers perform to get from one state to another (by boarding, riding, alighting, or walking)
- Each activity has an associated **time cost** (e.g., waiting is costly, walking takes time, riding is faster)
- **Passengers flow** a real number that represents the number of passengers like water from their origin to destination through these nodes and links during a certain time. This flow will be the result of the optimization model next week.

### Nodes

For each station, we create **4 different node types**:

1. **ACCESS nodes**
   - One for each station
   - Entry point to the network
   - From here passengers can board any line serving that station
   - Example: `"ACCESS$Bahnhof"`

2. **EGRESS nodes**
   - One for each station
   - Exit point of the network
   - To here passengers can alight from any line serving that station
   - Example: `"EGRESS$Bahnhof"`

3. **TRANSFER nodes**
   - One for each station
   - Represents a passenger transferring at a station
   - From here passengers can walk to other stations' transfer nodes or switch lines at this station
   - Example: `"TRANSFER$Bahnhof"`

4. **SERVICE nodes** (line-specific)
   - Represent the line serving that station in a specific direction
   - One per station per line per direction
   - Example: `"1-up-Bahnhof"` (Line 1, direction up, at Bahnhof)

### Links / Activities

Links in the network represent different passenger activities. Each link as a duration which the optimization model will consider together with a link type specific cost to calculate the optimal passenger flow. 

1. **BOARD**: Boarding a bus
2. **RIDE**: Riding the bus between stations
3. **ALIGHT**: Alighting from the bus
4. **WALK**: Walking between nearby stations for transfers

## Task 1: Implement network construction functions

You will implement four functions across two files:
1. Walkable distance calculation (`walkable_distance.py`)
2. Walking links between stations (`network.py`)
3. Direct walking links within stations (`network.py`)
4. Link creation for bus lines (`network.py`)

### Walkable distance calculation
Calculate which station pairs are close enough for passengers to walk between them.

**Location**: [src/openbus_light/manipulate/walkable_distance.py](../src/openbus_light/manipulate/walkable_distance.py)

**Function**: `find_all_walkable_distances(stations, parameters) -> tuple[WalkableDistance, ...]`

### Walking links between stations

Create bidirectional walking links between two different stations in the passenger flow network.

**Location**: [src/openbus_light/plan/network.py](../src/openbus_light/plan/network.py)

**Function**: `_create_links_for_walkable_distance(walkable_distance) -> tuple[...]`

### Direct walking links within stations

Create walking links that allow passengers to walk directly between stations from ACCESS and to EGRESS nodes without boarding a bus.

**Location**: [src/openbus_light/plan/network.py](../src/openbus_light/plan/network.py)

**Function**: `_create_links_for_direct_walking(stations) -> tuple[...]`

### Boarding, alighting, and riding links

Create all links connecting nodes for one direction of one bus line. The node creation part is already provided (you'll call `_create_nodes_for_direction()`). You need to implement the link creation logic.

**Location**: [src/openbus_light/plan/network.py](../src/openbus_light/plan/network.py)

**Function**: Link creation portion of `create_nodes_and_links_for_direction()`

## Task 2: Implement test functions

To verify your understanding of the network construction, you will implement four test functions in the test file.

**Location**: [test/test_network.py](../test/test_network.py)

**Test Functions**:
1. `test_direct_walking_links_created_for_all_stations` - Verify that direct walking links are correctly created
2. `test_links_for_direction_link_count()` - Verify the correct total number of links
3. `test_links_have_correct_activity_counts()` - Verify that links are created with correct activity types and counts
4. `test_simple_scenario_network_construction()` - Integration test for the complete network

Each test function includes docstrings with hints to guide your implementation. For calculating values, you should not hard-code the values you expect but calculate them with relation to the input scenario.

## Task 3: Write a Technical Report

Write a max. 2-page technical report explaining the passenger flow network structure. Your goal is to help a peer student understand how the network models passenger movement and why it's designed this way.

**Requirements**:
- Explain the 4 node types and why each is needed
- Describe the different link types (activities) and how they connect nodes
- Include illustrations to help with the explanation (e.g. showing network structure and passenger flow)
- Use a concrete example to demonstrate how passengers move through the network
- Describe limitations of the structure of the implemented passenger flow network and suggest possible improvements

**Format**:
- PDF format, maximum 2 pages
- Illustrations can be hand-drawn or digital

You have freedom to decide how to structure your explanations and what aspects to emphasize.

## Testing Your Implementation

After implementing your functions and tests, all tests in `test/test_network.py` should pass:

```bash
pytest test/test_network.py
```

**Note**: Passing tests don't guarantee correctness - ensure your logic is sound and matches the expected behavior.

## Deliverables

Submit the following files:

- [ ] [src/openbus_light/manipulate/walkable_distance.py](../src/openbus_light/manipulate/walkable_distance.py) - Implemented `find_all_walkable_distances()`
- [ ] [src/openbus_light/plan/network.py](../src/openbus_light/plan/network.py) - Implemented `_create_links_for_walkable_distance()`, `_create_links_for_direct_walking()`, and link creation in `_create_nodes_and_links_for_direction()`
- [ ] [test/test_network.py](../test/test_network.py) - Implemented three test functions
- [ ] `week2_report.pdf` - Technical report explaining the passenger flow network structure
- [ ] All tests pass: `test_network.py`

## Grading Rubric (25% of Final Grade)

**Task 1: Network Implementation**
- Correctness
- Code passes all unit tests
- Clean, readable code following Python conventions

**Task 2: Test Implementation**
- Correct test assertions
- Demonstrates understanding of network structure through tests

**Task 3: Technical Report**
- Clear explanation of the purpose and structure of the line planning network
- Quality and relevance of illustrations
- Demonstrates understanding by considering limitations of the current implementation


## Getting Help

**Office Hours:** Thursday afternoon, participate by choosing a time slot on Moodle

**Discussion Forum on Moodle:** Post your questions so everyone can profit from the answer!

**Debugging Tips:**
- Use the test file to understand and debug expected behavior, it can actually help to first write the test before doing the implementation
- Draw small examples (2-3 stations) by hand before coding
- Use the function network.debug_plot() on a PassengerFlowNetwork object to plot the network layout
