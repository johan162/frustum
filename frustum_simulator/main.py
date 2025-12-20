"""
Frustum Bucket Water Drainage Simulator

This module simulates the physics of water draining from a frustum-shaped bucket
using Torricelli's law and numerical integration.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List


class FrustumBucket:
    """
    Represents a frustum-shaped bucket with water drainage simulation.

    A frustum is a truncated cone with:
    - Upper radius: r1 (top opening)
    - Lower radius: r2 (bottom base)
    - Height: h (calculated from volume)
    - Outlet diameter: d (at center of bottom)
    """

    GRAVITY = 9.81  # m/s^2

    def __init__(self, r1: float, r2: float, volume: float, outlet_diameter: float):
        """
        Initialize the frustum bucket.

        Args:
            r1: Upper radius (m)
            r2: Lower radius (m)
            volume: Total volume of the bucket (L)
            outlet_diameter: Diameter of the outlet at the bottom (m)
        """
        self.r1 = r1
        self.r2 = r2
        self.volume_liters = volume
        self.volume_m3 = volume / 1000.0  # Convert liters to cubic meters
        self.outlet_diameter = outlet_diameter
        self.outlet_area = np.pi * (outlet_diameter / 2) ** 2

        # Calculate the height of the frustum from the given volume
        self.height = self._calculate_height()

    def _calculate_height(self) -> float:
        """
        Calculate the height of the frustum given its volume.

        Volume of a frustum: V = (π*h/3) * (r1² + r1*r2 + r2²)
        Solving for h: h = 3*V / (π * (r1² + r1*r2 + r2²))

        Returns:
            Height in meters
        """
        numerator = 3 * self.volume_m3
        denominator = np.pi * (self.r1**2 + self.r1 * self.r2 + self.r2**2)
        return numerator / denominator

    def radius_at_height(self, h: float) -> float:
        """
        Calculate the radius of the frustum at a given height from the bottom.

        Linear interpolation: r(h) = r2 + (r1 - r2) * (h / H)

        Args:
            h: Height from the bottom (m)

        Returns:
            Radius at height h (m)
        """
        return self.r2 + (self.r1 - self.r2) * (h / self.height)

    def cross_sectional_area(self, h: float) -> float:
        """
        Calculate the cross-sectional area at a given height.

        Args:
            h: Height from the bottom (m)

        Returns:
            Cross-sectional area (m²)
        """
        r = self.radius_at_height(h)
        return np.pi * r**2

    def flow_rate(self, h: float) -> float:
        """
        Calculate the volumetric flow rate using Torricelli's law.

        Torricelli's law: v = √(2*g*h)
        Flow rate: Q = A_outlet * v = A_outlet * √(2*g*h)

        Args:
            h: Current water height from the bottom (m)

        Returns:
            Flow rate (m³/s)
        """
        if h <= 0:
            return 0.0
        velocity = np.sqrt(2 * self.GRAVITY * h)
        return self.outlet_area * velocity

    def simulate(self, time_step: float) -> Tuple[List[float], List[float]]:
        """
        Simulate the water drainage process.

        Uses Euler's method to solve the differential equation:
        dh/dt = -Q(h) / A(h)

        where Q(h) is the flow rate and A(h) is the cross-sectional area.

        Args:
            time_step: Time step for numerical integration (seconds)

        Returns:
            Tuple of (time_points, height_points) lists
        """
        time_points = [0.0]
        height_points = [self.height]

        current_time = 0.0
        current_height = self.height

        # Continue until the bucket is essentially empty
        while current_height > 1e-6:  # Stop when height is very small
            # Calculate flow rate and cross-sectional area
            Q = self.flow_rate(current_height)
            A = self.cross_sectional_area(current_height)

            # Calculate the rate of change of height
            dh_dt = -Q / A

            # Update height using Euler's method
            current_height += dh_dt * time_step
            current_time += time_step

            # Ensure height doesn't go negative
            if current_height < 0:
                current_height = 0

            time_points.append(current_time)
            height_points.append(current_height)

            # Safety check to prevent infinite loops
            if current_time > 10000:  # 10,000 seconds max
                break

        return time_points, height_points

    def plot_simulation(self, time_points: List[float], height_points: List[float]):
        """
        Create a plot of water height vs time.

        Args:
            time_points: List of time values (seconds)
            height_points: List of corresponding height values (meters)
        """
        plt.figure(figsize=(10, 6))
        plt.plot(time_points, height_points, 'b-', linewidth=2)
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('Water Height (meters)', fontsize=12)
        plt.title('Water Drainage from Frustum Bucket', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.xlim(left=0)
        plt.ylim(bottom=0)

        # Add annotations
        total_time = time_points[-1]
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Empty')
        plt.axhline(y=self.height, color='g', linestyle='--', alpha=0.5, label='Full')
        plt.legend()

        # Add text box with parameters
        textstr = f'Parameters:\n'
        textstr += f'Upper radius (r₁): {self.r1:.3f} m\n'
        textstr += f'Lower radius (r₂): {self.r2:.3f} m\n'
        textstr += f'Volume: {self.volume_liters:.2f} L\n'
        textstr += f'Height: {self.height:.3f} m\n'
        textstr += f'Outlet diameter: {self.outlet_diameter:.4f} m\n'
        textstr += f'Total time: {total_time:.2f} s'

        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(0.98, 0.97, textstr, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=props, family='monospace')

        plt.tight_layout()
        plt.show()


def get_float_input(prompt: str, min_value: float = 0.0) -> float:
    """
    Get a valid float input from the user.

    Args:
        prompt: The prompt to display
        min_value: Minimum acceptable value

    Returns:
        Valid float value
    """
    while True:
        try:
            value = float(input(prompt))
            if value <= min_value:
                print(f"Value must be greater than {min_value}. Please try again.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def main():
    """Main entry point for the frustum bucket simulator."""
    print("=" * 60)
    print("FRUSTUM BUCKET WATER DRAINAGE SIMULATOR")
    print("=" * 60)
    print("\nThis program simulates water draining from a frustum-shaped")
    print("bucket under ideal conditions using Torricelli's law.\n")

    # Get user inputs
    print("Please enter the following parameters:\n")

    r1 = get_float_input("Upper radius r1 (meters): ")
    r2 = get_float_input("Lower radius r2 (meters): ")

    # Validate that r1 > r2 for a frustum
    while r1 <= r2:
        print("Upper radius must be greater than lower radius for a frustum.")
        r1 = get_float_input("Upper radius r1 (meters): ")
        r2 = get_float_input("Lower radius r2 (meters): ")

    volume = get_float_input("Total volume L (liters): ")
    d = get_float_input("Outlet diameter d (meters): ")
    t = get_float_input("Time step t (seconds): ", min_value=0.0)

    # Validate time step
    while t > 1.0:
        print("Warning: Large time step may reduce accuracy.")
        response = input("Continue with this time step? (y/n): ")
        if response.lower() == 'y':
            break
        t = get_float_input("Time step t (seconds): ", min_value=0.0)

    print("\n" + "=" * 60)
    print("Starting simulation...")
    print("=" * 60 + "\n")

    # Create bucket and run simulation
    bucket = FrustumBucket(r1, r2, volume, d)

    print(f"Calculated bucket height: {bucket.height:.4f} m")
    print(f"Outlet area: {bucket.outlet_area:.6f} m²")
    print(f"\nSimulating with time step: {t} seconds\n")

    # Run simulation
    time_points, height_points = bucket.simulate(t)

    # Get total drainage time
    total_time = time_points[-1]

    print("=" * 60)
    print(f"RESULT: {total_time:.2f} seconds")
    print("=" * 60)
    print(f"\nThe bucket takes {total_time:.2f} seconds to empty completely.\n")

    # Plot results
    print("Generating plot...")
    bucket.plot_simulation(time_points, height_points)


if __name__ == "__main__":
    main()
