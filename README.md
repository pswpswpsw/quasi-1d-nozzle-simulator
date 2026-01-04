# Quasi-1D Nozzle Flow Simulator

A modern, interactive web application for simulating compressible flow through rocket nozzles using quasi-1D flow theory.

## 🚀 Features

- **Interactive Flow Visualization**: Real-time Mach number and pressure ratio profiles with hover tooltips
- **Multiple Flow Regimes**: 
  - Subsonic Throat
  - Sonic Throat with Normal Shock Inside Expansion
  - Sonic Throat with Oblique Shock at Exit
  - Sonic Throat with Expansion Fan at Exit
- **Nozzle Geometry Control**: Adjustable parameters using `rocketisp` geometry model
- **Professional UI**: Modern dark theme with interactive plots and organized controls
- **Critical Pressure Ratios**: Automatic calculation and display of three critical pressure ratios

## 📋 Requirements

- Python 3.11+
- `uv` package manager (recommended) or `pip`

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/pswpswpsw/quasi-1d-nozzle-simulator.git
cd quasi-1d-nozzle-simulator
```

2. Install dependencies using `uv`:
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Running the Streamlit App

From the project root:
```bash
cd streamlit_app
uv run streamlit run app.py
```

Or:
```bash
uv run streamlit run streamlit_app/app.py
```

The app will open in your browser at `http://localhost:8501`.

### Using the Interactive Notebook

Open `nozzle_subsonic_v2_interactive.ipynb` in Jupyter Lab/Notebook for an interactive notebook experience.

## 📁 Project Structure

```
.
├── streamlit_app/          # Streamlit web application
│   ├── app.py             # Main application file
│   ├── nozzle.py          # Nozzle class with flow simulation
│   ├── geometry.py        # Geometry helper functions
│   └── README.md          # App-specific documentation
├── nozzle_subsonic_v2_interactive.ipynb  # Interactive Jupyter notebook
├── pyproject.toml         # Project dependencies
└── README.md              # This file
```

## 🎨 UI Features

- **Modern Dark Theme**: Professional ChatGPT-style interface
- **Wider Plot Layout**: Plot takes 70-75% of screen width for better visibility
- **Hover Tooltips**: Display x, M, p/p₀, and r values on hover
- **Interactive Legend**: Click legend items to toggle curves
- **Parameter Groups**: Organized geometry controls with visual grouping
- **Numeric Inputs**: Sliders with accompanying number input boxes

## 🚀 Deployment

### Streamlit Cloud

1. Fork this repository or push it to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select your repository
4. Set the main file path to `streamlit_app/app.py`
5. Streamlit Cloud will automatically detect `requirements.txt` and install dependencies

The app will be available at `https://your-app-name.streamlit.app`

## 🔬 Technical Details

The simulator implements:
- Isentropic flow relations
- Normal shock relations
- Oblique shock theory
- Prandtl-Meyer expansion fans
- Area-Mach number relations

## 👤 Author

**Prof. Shaowu Pan**  
Rensselaer Polytechnic Institute

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Uses `rocketisp` library for nozzle geometry modeling
- Built with Streamlit, Plotly, NumPy, and SciPy
