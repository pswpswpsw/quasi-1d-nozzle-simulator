# 1D Nozzle Simulator - Streamlit App

This is a Streamlit web application for simulating quasi-1D flow through a nozzle. It's converted from the interactive Jupyter notebook `nozzle_subsonic_v2_interactive.ipynb`.

## Features

- Interactive pressure ratio control via slider
- Real-time flow profile visualization
- Support for multiple flow regimes:
  - Subsonic Throat
  - Sonic Throat with Normal Shock Inside Expansion
  - Sonic Throat with Oblique Shock at Exit
  - Sonic Throat with Expansion Fan at Exit
- Displays critical pressure ratios
- Shows Mach number, pressure ratio, and nozzle geometry

## Installation

The app uses the same dependencies as the parent project. From the parent directory:

```bash
uv sync
```

## Running the App

From the `streamlit_app` directory:

```bash
cd streamlit_app
uv run streamlit run app.py
```

Or from the parent directory:

```bash
uv run streamlit run streamlit_app/app.py
```

The app will open in your default web browser at `http://localhost:8501`.

## Usage

1. Use the slider in the sidebar to adjust the back pressure ratio (p_b/p_0)
2. The flow regime will automatically update based on the pressure ratio
3. The plot shows:
   - Green line: Mach number M(x)
   - Orange dashed line: Pressure ratio p/p_0(x)
   - Black line: Nozzle radius (on secondary axis)
   - Red lines: Shock waves (when applicable)
   - Blue dashed lines: Expansion fan rays (when applicable)

## Files

- `app.py` - Main Streamlit application
- `nozzle.py` - Nozzle class with flow simulation logic
- `geometry.py` - Geometry helper functions for nozzle area profile

## Author

Shaowu Pan

