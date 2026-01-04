# Copilot Instructions for 1D Nozzle Flow Simulator

## Project Overview
This codebase simulates quasi-1D compressible flow in nozzles using Python. It consists of Jupyter notebooks demonstrating subsonic and supersonic flow regimes through a Laval nozzle.

## Architecture
- **Core Component**: `Nozzle` class in `nozzle_subsonic_v2.ipynb` encapsulates nozzle geometry, flow calculations, and visualization
- **Geometry**: Area profile defined by function `A(x) = 3*(x-0.6)**2 + 0.25` (normalized x from 0 to 1)
- **Flow Regimes**: Handles subsonic, transonic, and supersonic flows with critical pressure ratios
- **Key Calculations**: Mach number solving via `scipy.optimize.root_scalar`, isentropic relations

## Key Patterns
- **Mach Number Solving**: Use `scipy.optimize.root_scalar` with `method='brentq'` for area-Mach relation: `m**2 * ratio**2 - (2/(gamma+1)*(1+(gamma-1)/2*m**2))**((gamma+1)/(gamma-1))`
- **Critical Ratios**: Compute pressure ratios for choke, normal shock, and shock-free conditions using isentropic formulas
- **Plotting**: Matplotlib with grid enabled, labels sized 15-25, xlim/ylim set appropriately
- **Constants**: gamma=1.4, R=287 J/kg·K for air

## Workflows
- **Development**: Edit notebooks in VS Code, run cells sequentially
- **Visualization**: Use `nozzle.plot_area_profile()` and `nozzle.plot_flow_profile(pb_p0_ratio)` for geometry and flow plots
- **Dependencies**: Install via `uv sync`, includes scipy, numpy, matplotlib; dev group has ipykernel

## Conventions
- **Variable Naming**: `p_0` for total pressure, `p_b` for back pressure, `M_array` for Mach number arrays
- **Units**: SI units (Pa, K, m/s, kg/m³)
- **Error Handling**: Use `scipy.optimize` tolerances `xtol=1e-7, rtol=1e-7`
- **Throat Finding**: `scipy.optimize.fmin` on area function to locate minimum

## Examples
- **Create Nozzle**: `nozzle = Nozzle(A, xmin=0, xmax=1, gamma=1.4)`
- **Solve Mach**: `m = nozzle.solve_mach_number_from_area_ratio(ratio, gamma, is_subsonic=True)`
- **Plot Flow**: `nozzle.plot_flow_profile(0.972)` for subsonic case

Reference: `nozzle_subsonic_v2.ipynb` for complete implementation patterns.