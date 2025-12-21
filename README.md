# Frustum Bucket Water Drainage Simulator

[![GitHub release](https://img.shields.io/github/v/release/johan162/frustum?include_prereleases)](https://github.com/johan162/frustum/releases) 
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-dependency%20manager-blue)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: flake8](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A physics-based simulation of fluid draining from a frustum-shaped bucket with **realistic effects** including discharge coefficient and viscosity, using **Torricelli's law** and numerical integration methods.

### 🆕 Features
- **Discharge Coefficient (Cd)**: Accounts for real-world flow reduction (vena contracta, edge effects)
- **Fluid Viscosity**: Supports multiple fluid types (water, petrol, oil, treacle, honey, milk)
- **Reynolds Number Correction**: Adjusts flow based on laminar/turbulent conditions
- **Side-by-Side Comparison**: Visual comparison of ideal vs. realistic drainage

## 📋 Table of Contents

- [Overview](#overview)
- [Physics Background](#physics-background)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Parameters](#parameters)
- [Example Output](#example-output)
- [Development](#development)
- [Contributing](#contributing)

## 🔭 Overview

This program simulates the drainage of water from a **frustum** (truncated cone) shaped bucket through a circular outlet at the bottom center. The simulation uses principles from fluid dynamics to accurately model how the water level decreases over time.

### What is a Frustum?

A frustum is a portion of a cone that lies between two parallel planes cutting it. In this case, it's a bucket with:
- A larger circular opening at the top (radius `r1`)
- A smaller circular base at the bottom (radius `r2`)
- A specific volume capacity (`L` in liters)

<img src="frustum-bucket.png" alt="Typical Frustum Bucket" width="200">

***Figure 1: Frustum bucket***


## 🔬 Physics Background

### Governing Equations

The simulation is based on the following physical principles:

#### 1. Frustum Volume

The volume of a frustum is given by:

```
V = (π × h / 3) × (r₁² + r₁×r₂ + r₂²)
```

where:
- `V` = volume (m³)
- `h` = height of the frustum (m)
- `r₁` = upper radius (m)
- `r₂` = lower radius (m)

Given the volume `L`, we can solve for the height:

```
h = 3V / (π × (r₁² + r₁×r₂ + r₂²))
```

#### 2. Torricelli's Law

**Torricelli's law** states that the speed of efflux of a fluid through a sharp-edged orifice at the bottom of a tank filled to a depth `h` is the same as the speed that a body would acquire in free fall through a height `h`:

```
v = √(2gh)
```

where:
- `v` = velocity of water exiting the outlet (m/s)
- `g` = gravitational acceleration (9.81 m/s²)
- `h` = height of water above the outlet (m)

#### 3. Volumetric Flow Rate

The volumetric flow rate through the outlet is:

```
Q = A_outlet × v = π(d/2)² × √(2gh)
```

where:
- `Q` = volumetric flow rate (m³/s)
- `A_outlet` = cross-sectional area of the outlet (m²)
- `d` = outlet diameter (m)

#### 4. Rate of Height Change

The rate at which the water level drops depends on the flow rate and the cross-sectional area at the current water height:

```
dh/dt = -Q / A(h)
```

where:
- `A(h)` = cross-sectional area at height `h` (m²)
- The negative sign indicates the water level is decreasing

For a frustum, the radius at height `h` is:

```
r(h) = r₂ + (r₁ - r₂) × (h / H)
```

And the cross-sectional area is:

```
A(h) = π × r(h)²
```

#### 5. Realistic Flow Corrections

##### Discharge Coefficient (Cd)
Real orifices don't achieve ideal flow due to:
- **Vena contracta**: Flow stream contracts after leaving the orifice
- **Edge effects**: Sharp edges create turbulence and energy losses
- **Viscous losses**: Fluid friction reduces flow rate

Typical Cd values:
```
Cd = 1.0   → Ideal flow (theoretical only)
Cd = 0.8   → Smooth, rounded orifice
Cd = 0.65  → Typical sharp-edged orifice
Cd = 0.6   → Sharp edge with significant contraction
```

The corrected velocity becomes:
```
v = Cd × √(2gh)
```

##### Viscosity Correction
Flow behavior depends on the **Reynolds number** (Re):

```
Re = v × d / ν
```

where `ν` is kinematic viscosity (m²/s).

Flow regimes:
- **Laminar (Re < 2300)**: Smooth, ordered flow with significant viscous effects
- **Transitional (2300 < Re < 4000)**: Mixed regime
- **Turbulent (Re > 4000)**: Chaotic flow with reduced viscous effects

Viscosity correction factors:
```
Re < 2300:  factor = 0.70  (70% of ideal)
Re < 4000:  factor = 0.85  (85% of ideal)
Re > 4000:  factor ≈ 1.0   (minimal viscosity effect)
```

#### 6. Numerical Integration

We solve the differential equation using **Euler's method**:

```
h(t + Δt) = h(t) + (dh/dt) × Δt
```

This is repeated for each time step `Δt` until the bucket is empty.

## ✨ Features

### Physics & Realism
- **Accurate Physics Simulation**: Uses Torricelli's law and proper fluid dynamics
- **Discharge Coefficient**: Adjustable Cd parameter (0.5-1.0) for realistic flow
- **Multiple Fluids**: Choose from water, petrol, milk, motor oil, olive oil, treacle, or honey
- **Viscosity Effects**: Automatic Reynolds number calculation and flow corrections
- **Laminar/Turbulent Flow**: Adapts to flow regime based on conditions

### Simulation Features
- **Numerical Integration**: Employs Euler's method with configurable time steps
- **Interactive Input**: Prompts for all necessary parameters with fluid selection
- **Comparison Mode**: Side-by-side plots of ideal vs. realistic drainage
- **Visualization**: Professional matplotlib graphs with parameter annotations
- **Detailed Output**: Displays calculated parameters, Reynolds numbers, and drainage times

### Example output plot

<img src="b_r07_r03_d002.png" alt="Output plot r1=0.7, r2=0.3, d=0.002" width="800">

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- Poetry (for dependency management)

### Install Poetry

If you don't have Poetry installed, install it using:

**Package manager:**

```bash
# macOS
brew install python poetry
```

**Directly:**

```bash
# Linux / WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Clone and Install

```bash
# Clone the repository (or navigate to the project directory)
cd frustum-bucket-simulator

# Install dependencies
poetry install
```

This will:
1. Create a virtual environment
2. Install all required dependencies (numpy, matplotlib)
3. Install development dependencies (black, flake8)
4. Install the package in editable mode

## 🚀 Usage

### Running the Simulator

#### Using Poetry:

```bash
poetry run frustum-sim
```

#### Or activate the virtual environment and run directly

```bash
source .venv/bin/activate
frustum-sim
```

#### Or run as a python module:

```bash
poetry run python -m frustum_simulator.main
```

### Interactive Prompts

The program will prompt you for the following parameters:

1. **Upper radius (r1)** in meters - the radius at the top of the bucket
2. **Lower radius (r2)** in meters - the radius at the bottom of the bucket
3. **Total volume (L)** in liters - the capacity of the bucket
4. **Outlet diameter (d)** in meters - the diameter of the drainage hole
5. **Fluid type** - select from water, petrol, milk, motor oil, olive oil, treacle, or honey
6. **Discharge coefficient (Cd)** - real-world flow correction (0.5-1.0)
7. **Simulation mode** - realistic only or side-by-side comparison with ideal
8. **Time step (t)** in seconds - the simulation time step for numerical integration

### Input Validation

The program includes validation to ensure:
- All values are positive numbers
- Upper radius is greater than lower radius (required for a frustum)
- Time step is reasonable (warns if > 1 second for accuracy)

## 📊 Parameters

| Parameter | Symbol | Unit | Description | Typical Range |
|-----------|--------|------|-------------|---------------|
| Upper radius | r1 | meters | Radius at the top opening | 0.1 - 1.0 m |
| Lower radius | r2 | meters | Radius at the bottom base | 0.05 - 0.5 m |
| Volume | L | liters | Total bucket capacity | 1 - 100 L |
| Outlet diameter | d | meters | Diameter of drainage hole | 0.001 - 0.05 m |
| Discharge coeff | Cd | dimensionless | Flow reduction factor | 0.5 - 1.0 |
| Fluid type | - | - | Fluid being drained | See list below |
| Time step | t | seconds | Simulation time increment | 0.01 - 0.1 s |

### Available Fluids

| Fluid | Density (kg/m³) | Dynamic Viscosity (Pa·s) | Typical Use |
|-------|-----------------|--------------------------|-------------|
| Water | 1000 | 0.001 | General purpose |
| Petrol | 750 | 0.0006 | Low viscosity reference |
| Milk | 1030 | 0.002 | Similar to water |
| Motor Oil | 870 | 0.29 | High viscosity |
| Olive Oil | 910 | 0.081 | Medium viscosity |
| Treacle | 1420 | 5.0 | Very high viscosity |
| Honey | 1420 | 10.0 | Extremely high viscosity |
### Comparison Mode (Ideal vs. Realistic)

```
======================================================================
FRUSTUM BUCKET DRAINAGE SIMULATOR (Real-World Effects)
======================================================================

This program simulates fluid draining from a frustum-shaped bucket
with realistic effects: discharge coefficient and viscosity.

Please enter the following parameters:

Upper radius r1 (meters): 0.15
Lower radius r2 (meters): 0.10
Total volume L (liters): 10
Outlet diameter d (meters): 0.01

Available fluids:
  1. Water                 (viscosity: 1.00 mPa·s)
  2. Petrol (Gasoline)     (viscosity: 0.60 mPa·s)
  3. Milk                  (viscosity: 2.00 mPa·s)
  4. Motor Oil (SAE 30)    (viscosity: 290.0 mPa·s)
  5. Olive Oil             (viscosity: 81.0 mPa·s)
  6. Treacle (Golden Syrup)(viscosity: 5.0 mPa·s)
  7. Honey                 (viscosity: 10.0 mPa·s)

Select fluid (1-7): 1

Discharge coefficient (Cd):
  • 1.0  = Ideal flow (theoretical)
  • 0.8  = Smooth, rounded orifice
  • 0.65 = Typical sharp-edged orifice
  • 0.6  = Sharp-edged with vena contracta
Enter discharge coefficient (0.5-1.0): 0.65

Simulation mode:
  1. Realistic only
  2. Side-by-side comparison (Ideal vs Realistic)
Select mode (1 or 2, default 2): 2

Time step t (seconds): 0.05

======================================================================
Starting simulation...
======================================================================

Bucket configuration:
  Calculated height: 0.3395 m
  Outlet area: 0.000079 m²
  Fluid: Water
  Discharge coefficient: 0.65
  Time step: 0.05 seconds

Running ideal simulation...
Running realistic simulation...

======================================================================
RESULTS:
======================================================================
Ideal drainage time:     245.67 seconds
Realistic drainage time: 377.95 seconds
Time increase:           +132.28 seconds (53.9%)
======================================================================

Generating comparison plot...
```

The program displays a side-by-side plot showing both ideal and realistic drainage curves, with parameter information below.


The program will then display a graph showing:
- Water height (m) on the y-axis
- Time (seconds) on the x-axis
- A smooth curve showing the drainage process
- Parameter information in a text box
- Grid lines for easy reading

### Understanding the Graph

The drainage curve is **non-linear** because:
1. As water level decreases, the flow rate decreases (√h relationship)
2. The cross-sectional area changes with height (frustum shape)
3. Both effects combine to create a characteristic drainage curve

The curve typically shows:
- **Fast drainage initially** when the water level is high (higher pressure)
- **Slower drainage at the end** as the water level approaches zero

## 🛠️ Development

### Code Quality Tools

This project uses:

- **black**: Automatic code formatting
- **flake8**: Linting and style checking

### Running Code Quality Checks

```bash
# Format code with black
poetry run black frustum_simulator/

# Check with flake8
poetry run flake8 frustum_simulator/

# Run both
poetry run black frustum_simulator/ && poetry run flake8 frustum_simulator/
```

### Project Structure

```
frustum-bucket-simulator/
├── frustum_simulator/
│   ├── __init__.py      # Package initialization
│   └── main.py          # Main simulation code
├── pyproject.toml       # Poetry configuration and dependencies
├── README.md            # This file
└── poetry.lock          # Locked dependency versions (after install)
```

### Adding Dependencies

```bash
# Add a new runtime dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name
```

**Note**: The program requires r1 > r2

## 📝 Physics Assumptions

This simulation makes the following ideal assumptions:

1. **No air resistance**: Air drag is negligible
2. **Sharp-edged orifice**: The outlet is a perfect circular hole
3. **Steady flow**: No turbulence or vortex formation
4. **Rigid container**: The bucket doesn't deform
5. **Constant gravity**: g = 9.81 m/s²

In reality:
- Surface tension and vortex effects may play a role

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add 3D visualization of the frustum
- Export data to CSV for analysis
- Add unit tests
- Add support for different shapes (cylinder, cone, sphere)
- Add support for inverted bucket, i.e. allow r1 < r2
>

## 📄 License

This project is licensed under the MIT License - feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Based on **Torricelli's theorem** (Evangelista Torricelli, 1643)
- Numerical methods from computational fluid dynamics
- Matplotlib for visualizations

## 📚 References

- Munson, B. R., et al. (2013). *Fundamentals of Fluid Mechanics* (7th ed.). Wiley.

---

**Made with ❤️ and Physics**

For questions or issues, please open an issue on the repository.
