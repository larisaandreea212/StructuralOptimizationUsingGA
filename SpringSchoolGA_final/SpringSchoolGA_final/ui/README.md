# GA Dashboard (Python UI)

This UI allows you to:

- configure GA parameters (`algorithm_settings.txt`)
- run the C++ executable
- store experiment runs with metadata labels:
  - fitness function
  - selection method
  - crossover method
- compare experiments with graphs:
  - fitness evolution per epoch
  - final fitness impact by fitness function
  - final fitness impact by selection + crossover combination
  - runtime and profiling impact

## 1) Install dependencies

From project root:

```bash
pip install -r ui/requirements.txt
```

## 2) Run the UI

```bash
streamlit run ui/app.py
```

## 3) Build/run integration notes

- The default executable path used by the UI is:
  - `build/Release/ChronoProject_FinalGA.exe`
- If your executable is elsewhere, set it in the UI field before running.
- Each run writes current settings to:
  - `build/algorithm_settings.txt`

## 4) Experiment persistence

Saved files are stored in:

- `ui/experiments/registry.json`
- `ui/experiments/*.csv` (snapshots for GA values and optional profiling)

## 5) Profiling CSV format (recommended)

To power the profiling stage chart, upload CSV files with:

- `stage` (example: `Evaluate`, `Selection`, `Crossover`, `Mutation`)
- `seconds` (float value)

Example:

```csv
stage,seconds
Evaluate,22.53
Selection,0.21
Crossover,0.12
Mutation,0.09
```
