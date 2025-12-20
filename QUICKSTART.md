# Quick Start Guide

## Installation

### Option 1: Using requirements.txt (Recommended for quick start)

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Poetry

```bash
# Install Poetry first if needed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run with Poetry
poetry run frustum-sim
```

## Running the Program

### Quick Test Run

To test the program with predefined parameters:

```bash
python test_simulation.py
```

This will run a simulation with:
- Upper radius: 0.15 m (15 cm)
- Lower radius: 0.10 m (10 cm)
- Volume: 10 liters
- Outlet diameter: 0.01 m (1 cm)
- Time step: 0.05 seconds

### Interactive Mode

To run with custom parameters:

```bash
python -m frustum_simulator.main
```

Or if using Poetry:

```bash
poetry run frustum-sim
```

## Example Session

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

## Understanding the Results

The program calculates:
1. **Bucket height** - derived from the given volume and radii
2. **Outlet area** - cross-sectional area of the drainage hole
3. **Drainage time** - total seconds to empty (with 2 decimal precision)
4. **Visualization** - matplotlib graph showing water level over time

## Tips

- **Time step**: Smaller values (0.01-0.05 s) give more accurate results
- **Units**: All inputs are in SI units (meters, liters, seconds)
- **Graph**: Close the matplotlib window to exit the program
- **Accuracy**: Results assume ideal conditions (no viscosity, perfect outlet)

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'numpy'` or similar:

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate  # Or poetry shell

# Install dependencies
pip install -r requirements.txt  # Or poetry install
```

### Display Issues with matplotlib

If the plot doesn't display:

```bash
# On macOS, you may need to set the backend
export MPLBACKEND=TkAgg

# Then run the program
python -m frustum_simulator.main
```

### Permission Denied

If you get permission errors:

```bash
chmod +x test_simulation.py
```

## Code Quality

The code has been formatted and checked with:
- **black**: Python code formatter (line length: 88)
- **flake8**: Style guide enforcement (PEP 8 compliant)

To check code quality yourself:

```bash
# If you have black and flake8 installed
black frustum_simulator/
flake8 frustum_simulator/
```
