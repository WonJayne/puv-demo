# Week 4: Scenario Analysis & Sensitivity Studies

## Overview

This week, you will conduct a sensitivity analysis to understand how the optimal line planning solution responds to different operational scenarios and assumptions. While the line routes and stop patterns remain fixed, you will investigate how changing conditions affect optimal frequency decisions, capacity utilization, costs, and service quality.

By the end of this week, you will:
- Implement a realistic baseline scenario
- Implement parameter modifications to model a specific scenario
- Run optimization experiments under changed conditions
- Analyze the impacts on the line planning solution
- Compare your scenario results with the baseline solution
- Document your findings in a comprehensive report

**Time Estimate:** 12 hours per team (6 hours per student)

## Learning Objectives

By the end of Week 4, you should be able to:
1. Conduct sensitivity analysis on optimization models by systematically varying parameters
2. Interpret optimization results to understand trade-offs between service quality and operating costs
3. Explain how model parameters influence optimal solutions in public transport planning
4. Communicate technical findings clearly through visualizations and written analysis

## Background: Sensitivity Analysis in Line Planning

The line planning optimization you implemented in Week 3 depends on numerous parameters that represent operational assumptions, cost structures, and passenger behavior. In practice, these parameters are often uncertain or subject to change:

- **Cost structures** may change with new technologies (e.g., autonomous vehicles, e-bikes)
- **Passenger behavior** varies with weather conditions and infrastructure
- **Demand levels** fluctuate over time and with policy changes
- **Value-of-time coefficients** reflect subjective preferences about different activities

Sensitivity analysis helps us understand:
- How robust is the current solution to parameter changes?
- Which parameters have the strongest influence on outcomes?
- What operational adjustments are needed under different conditions?

## Task 1: Establish Baseline with Realistic Parameters

Before analyzing your scenario, you must first establish a **realistic baseline** using well-justified parameters. The default parameters in the code are placeholders and may not reflect real-world conditions.

**Your Task:**
1. Research realistic values for the key line planning parameters from academic literature, industry reports, or transport authority guidelines
2. Justify each parameter choice with references to the literature or real-world data
3. Implement a baseline experiment with your justified parameters
4. Document your parameter choices and justifications in your report

**In Your Report:**
Include a **parameter table** with columns:
- Parameter name
- Chosen value
- Source/reference or short justification

This baseline will serve as your reference point for comparing the impact of your assigned scenario.

## Task 2: Implement Your Assigned Scenario

Each group will be assigned **one of the four scenarios** described below. Your task is to:

1. Understand the scenario description and its modeling implications
2. Determine which parameters need to be modified
3. Implement the parameter changes in code
4. Run the optimization with multiple parameters to find the solutions under the new conditions
5. Analyze and document the results

### Scenario Descriptions

#### Scenario 1: Pod-City
Autonomous minibuses (pods) are introduced with a different operating cost structure. These vehicles have similar capacity to minibuses (e.g., 10 seats) but lower operating costs due to automation.

*Example Analysis Questions:*
- How does the reduced operating cost affect optimal frequencies?
- What is the effect of the increased frequencies?
- How does vehicle utilization change?

#### Scenario 2: E-Bike-City
E-bikes become the primary access/egress mode instead of walking. This affects both travel speeds and the direct network connectivity.

*Example Analysis Questions:*
- How does increased access/egress range affect line planning?
- How does the optimal frequency distribution change?

#### Scenario 3: Increased Modal Split
Public transport demand doubles.

*Example Analysis Questions:*
- What frequency adjustments are needed to accommodate doubled demand?
- What is the impact on required fleet size?

#### Scenario 4: Rainy Day Scenario

**Context:** Poor weather conditions (heavy rain) make waiting and accessing stations more unpleasant. Passengers perceive waiting time and access/egress time as more costly under these conditions.

*Example Analysis Questions:*
- How does increased sensitivity to waiting affect the optimization model?
- Which lines see the largest frequency changes?

**Reference:** See [line_planning_experiments.py](../line_planning_experiments.py) for an example of running multiple experiments in parallel and generating comparative visualizations.

**Tips:**
- Use descriptive experiment IDs
- Save results to separate subdirectories
- Get inspiration form the existing plotting functions from `openbus_light.plot`
- Document parameter choices clearly
- You can use euler for running many experiments in parallel

## Task 3: Analysis and Report

Write a **2 to 4-page technical report** analyzing your scenario and its implications for line planning. Describe clearly which changes you have made.

**Important:** This is the final extension of your course report. Add a new section to your existing document (Weeks 1-3) that presents your scenario analysis. Your complete report should now tell the full story: demand and network (Weeks 1-2), optimization model (Week 3), and practical application through scenario analysis (Week 4). This comprehensive document will be your final submission for this part of the course.

**Format:**
- PDF format, 2 to 4 pages (+ report from other weeks)
- Professional presentation with clear figures and tables
- All visualizations must have captions and axis labels
- Ensure a coherent narrative throughout all sections

## Deliverables

Submit the following files:

- [ ] [exercises/week4_experiments.py](week4_experiments.py) - Your experiment script (should run on your git repo)
- [ ] `exercises/week4_report.pdf` - Complete technical report (final submission including all weeks)
- [ ] All experiments run successfully and generate results

## Grading Rubric (25% of Final Grade)

**Implementation & Experiments**
- Script runs successfully and generates results (in your own code base, i.e. you can make any changes you like to openbus_light)

**Visualizations**
- Clear, properly labeled figures
- Visualizations effectively support analysis

**Analysis & Report**
- Clear explanation of scenario and modeling choices
- Analysis of results with specific insights
- Demonstrates understanding of line planning trade-offs
- Professional presentation and writing quality
- Thoughtful discussion of limitations

## Getting Help

**Office Hours:** Thursday afternoon, participate by choosing a time slot on Moodle

**Discussion Forum on Moodle:** Post your questions so everyone can profit from the answer!
