#!/usr/bin/env python3
"""
Quick test of the frustum simulator with predefined values.
This allows testing without interactive input.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frustum_simulator.main import FrustumBucket

def test_simulation():
    """Run a quick test with predefined parameters."""
    print("=" * 60)
    print("FRUSTUM BUCKET SIMULATOR - TEST RUN")
    print("=" * 60)

    # Test parameters
    r1 = 0.15  # 15 cm top radius
    r2 = 0.10  # 10 cm bottom radius
    volume = 10  # 10 liters
    d = 0.01  # 1 cm outlet diameter
    t = 0.05  # 50 ms time step

    print(f"\nTest Parameters:")
    print(f"  Upper radius (r1): {r1} m")
    print(f"  Lower radius (r2): {r2} m")
    print(f"  Volume: {volume} L")
    print(f"  Outlet diameter: {d} m")
    print(f"  Time step: {t} s")

    # Create bucket and run simulation
    bucket = FrustumBucket(r1, r2, volume, d)

    print(f"\nCalculated bucket height: {bucket.height:.4f} m")
    print(f"Outlet area: {bucket.outlet_area:.6f} m²")
    print("\nRunning simulation...")

    # Run simulation
    time_points, height_points = bucket.simulate(t)

    # Get total drainage time
    total_time = time_points[-1]

    print("\n" + "=" * 60)
    print(f"RESULT: {total_time:.2f} seconds")
    print("=" * 60)
    print(f"\nThe bucket takes {total_time:.2f} seconds to empty.\n")

    # Verify simulation makes sense
    assert total_time > 0, "Drainage time should be positive"
    assert bucket.height > 0, "Bucket height should be positive"
    assert len(time_points) > 10, "Should have multiple simulation steps"

    print("✓ Test passed successfully!")
    print("\nNote: Close the matplotlib window to exit.")

    # Plot results
    bucket.plot_simulation(time_points, height_points)

if __name__ == "__main__":
    test_simulation()
