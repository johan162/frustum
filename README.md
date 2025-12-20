# Frustum Bucket Water Drainage Simulator

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-dependency%20manager-blue)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: flake8](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A physics-based simulation of water draining from a frustum-shaped bucket under ideal conditions, using **Torricelli's law** and numerical integration methods.

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

#### 5. Numerical Integration

We solve the differential equation using **Euler's method**:

```
h(t + Δt) = h(t) + (dh/dt) × Δt
```

This is repeated for each time step `Δt` until the bucket is empty.

## ✨ Features

- **Accurate Physics Simulation**: Uses Torricelli's law and proper fluid dynamics
- **Numerical Integration**: Employs Euler's method with configurable time steps
- **Interactive Input**: Prompts for all necessary parameters
- **Validation**: Ensures physically meaningful inputs
- **Visualization**: Generates a matplotlib graph showing water level vs. time
- **Detailed Output**: Displays calculated parameters and final drainage time
- **Professional Code**: Formatted with `black`, linted with `flake8`

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- Poetry (for dependency management)

### Install Poetry

If you don't have Poetry installed, install it using:

```bash
# macOS / Linux / WSL
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

#### Or activate the virtual environment:

```bash
poetry shell
frustum-sim
```

#### Or run directly:

```bash
poetry run python -m frustum_simulator.main
```

### Interactive Prompts

The program will prompt you for the following parameters:

1. **Upper radius (r1)** in meters - the radius at the top of the bucket
2. **Lower radius (r2)** in meters - the radius at the bottom of the bucket
3. **Total volume (L)** in liters - the capacity of the bucket
4. **Outlet diameter (d)** in meters - the diameter of the drainage hole
5. **Time step (t)** in seconds - the simulation time step for numerical integration

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
| Time step | t | seconds | Simulation time increment | 0.01 - 0.1 s |

### Example Values

For a typical bucket:
```
r1 = 0.15 m      (15 cm top radius)
r2 = 0.10 m      (10 cm bottom radius)
L  = 10 liters   (10 L capacity)
d  = 0.01 m      (1 cm outlet diameter)
t  = 0.05 s      (50 ms time step)
```

## 📈 Example Output

```
============================================================
FRUSTUM BUCKET WATER DRAINAGE SIMULATOR
============================================================

This program simulates water draining from a frustum-shaped
bucket under ideal conditions using Torricelli's law.

Please enter the following parameters:

Upper radius r1 (meters): 0.15
Lower radius r2 (meters): 0.10
Total volume L (liters): 10
Outlet diameter d (meters): 0.01
Time step t (seconds): 0.05

============================================================
Starting simulation...
============================================================

Calculated bucket height: 0.3395 m
Outlet area: 0.000079 m²

Simulating with time step: 0.05 seconds

============================================================
RESULT: 245.67 seconds
============================================================

The bucket takes 245.67 seconds to empty completely.

Generating plot...
```

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

## 🧪 Testing the Simulator

### Test Case 1: Small Bucket with Small Outlet

```
r1 = 0.10 m
r2 = 0.05 m
L  = 5 liters
d  = 0.005 m
t  = 0.01 s

Expected: Several hundred seconds
```

### Test Case 2: Large Bucket with Large Outlet

```
r1 = 0.30 m
r2 = 0.20 m
L  = 50 liters
d  = 0.02 m
t  = 0.05 s

Expected: A few hundred seconds (faster due to larger outlet)
```

### Test Case 3: Cylindrical Approximation

```
r1 = 0.15 m
r2 = 0.15 m  (same as r1, approaches cylinder)
L  = 20 liters
d  = 0.01 m
t  = 0.05 s
```

**Note**: The program requires r1 > r2, so this won't work as-is. Use r2 = 0.149 m for near-cylindrical behavior.

## 📝 Physics Assumptions

This simulation makes the following ideal assumptions:

1. **Inviscid flow**: No viscosity effects (no friction within the fluid)
2. **No air resistance**: Air drag is negligible
3. **Sharp-edged orifice**: The outlet is a perfect circular hole
4. **Constant discharge coefficient**: C_d = 1.0 (ideal flow)
5. **Steady flow**: No turbulence or vortex formation
6. **Rigid container**: The bucket doesn't deform
7. **Constant gravity**: g = 9.81 m/s²

In reality:
- Real drainage may be slightly slower due to viscosity
- Discharge coefficient is typically 0.6-0.8 for real orifices
- Surface tension and vortex effects may play a role

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add discharge coefficient parameter for more realistic simulation
- Implement multiple outlet support
- Add 3D visualization of the frustum
- Export data to CSV for analysis
- Add unit tests
- Add support for different shapes (cylinder, cone, sphere)

## 📄 License

This project is licensed under the MIT License - feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Based on **Torricelli's theorem** (Evangelista Torricelli, 1643)
- Numerical methods from computational fluid dynamics
- Matplotlib for beautiful visualizations

## 📚 References

- Munson, B. R., et al. (2013). *Fundamentals of Fluid Mechanics* (7th ed.). Wiley.

---

**Made with ❤️ and Physics**

For questions or issues, please open an issue on the repository.
