# Usage Guide

This repository contains two main exercises that demonstrate how to use the `openbus_light` toolkit.

## Working with `line_planning.py`

`line_planning.py` explores the line planning problem. The typical workflow is:

1. Ensure the dataset in `data/` is available.
2. Run the helper script which executes several configurations in parallel:
   ```bash
   python line_planning_experiments.py
   ```
   The results, including HTML plots, are written to the `results/` directory.
3. Inspect the generated plots in your web browser to analyse the impact of different parameters.

You can also run a single experiment manually:
```bash
python line_planning.py --help
```
This shows the available command line options such as the planning horizon, solver settings and output paths.
