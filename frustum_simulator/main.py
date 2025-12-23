"""
Frustum Bucket Water Drainage Simulator

This module simulates the physics of water draining from a frustum-shaped bucket
using Torricelli's law and numerical integration. Includes realistic effects such
as discharge coefficient and fluid viscosity.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class FluidProperties:
    """Properties of different fluids."""

    name: str
    density: float  # kg/m³
    dynamic_viscosity: float  # Pa·s
    kinematic_viscosity: float  # m²/s


# Common fluid properties at 20°C
FLUIDS: Dict[str, FluidProperties] = {
    "water": FluidProperties(
        name="Water", density=1000.0, dynamic_viscosity=0.001, kinematic_viscosity=1e-6
    ),
    "petrol": FluidProperties(
        name="Petrol (Gasoline)",
        density=750.0,
        dynamic_viscosity=0.0006,
        kinematic_viscosity=8e-7,
    ),
    "milk": FluidProperties(
        name="Milk",
        density=1030.0,
        dynamic_viscosity=0.002,
        kinematic_viscosity=1.94e-6,
    ),
    "motor_oil": FluidProperties(
        name="Motor Oil (SAE 30)",
        density=870.0,
        dynamic_viscosity=0.29,
        kinematic_viscosity=3.3e-4,
    ),
    "olive_oil": FluidProperties(
        name="Olive Oil",
        density=910.0,
        dynamic_viscosity=0.081,
        kinematic_viscosity=8.9e-5,
    ),
    "treacle": FluidProperties(
        name="Treacle (Golden Syrup)",
        density=1420.0,
        dynamic_viscosity=5.0,
        kinematic_viscosity=3.5e-3,
    ),
    "honey": FluidProperties(
        name="Honey", density=1420.0, dynamic_viscosity=10.0, kinematic_viscosity=7.0e-3
    ),
}


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

    def __init__(
        self,
        r1: float,
        r2: float,
        volume: float,
        outlet_diameter: float,
        discharge_coeff: float = 1.0,
        fluid: Optional[FluidProperties] = None,
    ):
        """
        Initialize the frustum bucket.

        Args:
            r1: Upper radius (m)
            r2: Lower radius (m)
            volume: Total volume of the bucket (L)
            outlet_diameter: Diameter of the outlet at the bottom (m)
            discharge_coeff: Discharge coefficient (0-1), default 1.0 (ideal)
            fluid: Fluid properties, default None (uses water)
        """
        self.r1 = r1
        self.r2 = r2
        self.volume_liters = volume
        self.volume_m3 = volume / 1000.0  # Convert liters to cubic meters
        self.outlet_diameter = outlet_diameter
        self.outlet_area = np.pi * (outlet_diameter / 2) ** 2
        self.discharge_coeff = discharge_coeff
        self.fluid = fluid if fluid else FLUIDS["water"]

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
        Calculate volumetric flow rate using Torricelli's law with corrections.

        Torricelli's law: v = Cd * √(2*g*h)
        Flow rate: Q = Cd * A_outlet * v

        Includes:
        - Discharge coefficient (Cd) for real-world effects
        - Viscosity correction using Reynolds number

        Args:
            h: Current water height from the bottom (m)

        Returns:
            Flow rate (m³/s)
        """
        if h <= 0:
            return 0.0

        # Base velocity from Torricelli's law
        velocity_ideal = np.sqrt(2 * self.GRAVITY * h)

        # Apply discharge coefficient
        velocity = self.discharge_coeff * velocity_ideal

        # Apply viscosity correction only for non-ideal conditions
        # (ideal conditions: Cd = 1.0, no viscosity effects)
        if self.discharge_coeff < 1.0:
            # Calculate Reynolds number for viscosity correction
            Re = self._reynolds_number(velocity, self.outlet_diameter)

            # Viscosity correction factor (empirical)
            if Re < 2300:  # Laminar flow
                viscosity_factor = 0.7
            elif Re < 4000:  # Transitional
                viscosity_factor = 0.85
            else:  # Turbulent (Re > 4000)
                viscosity_factor = 1.0 - (1000.0 / Re) if Re > 1000 else 0.5

            # Apply viscosity correction
            velocity *= viscosity_factor

        return self.outlet_area * velocity

    def _reynolds_number(self, velocity: float, diameter: float) -> float:
        """
        Calculate Reynolds number for flow through the outlet.

        Re = ρ * v * D / μ = v * D / ν

        Args:
            velocity: Flow velocity (m/s)
            diameter: Outlet diameter (m)

        Returns:
            Reynolds number (dimensionless)
        """
        return velocity * diameter / self.fluid.kinematic_viscosity

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

    @staticmethod
    def calculate_derivative(
        time_points: List[float], height_points: List[float]
    ) -> List[float]:
        """
        Calculate the derivative (rate of change) of height with respect to time.

        Args:
            time_points: List of time values (seconds)
            height_points: List of corresponding height values (meters)

        Returns:
            List of dh/dt values (meters/second)
        """
        return np.gradient(height_points, time_points).tolist()

    def plot_simulation(
        self,
        time_points: List[float],
        height_points: List[float],
        show_derivative: bool = False,
    ):
        """
        Create a plot of water height vs time.

        Args:
            time_points: List of time values (seconds)
            height_points: List of corresponding height values (meters)
            show_derivative: Whether to show rate of change subplot
        """
        if show_derivative:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
        else:
            ax1 = plt.gca()
            ax2 = None  # Initialize to avoid Pylance unbound warning

        # Main height plot
        ax1.plot(time_points, height_points, "b-", linewidth=2)
        ax1.set_xlabel("Time (seconds)", fontsize=12)
        ax1.set_ylabel("Water Height (meters)", fontsize=12)

        # Title includes fluid type if not ideal
        title = "Water Drainage from Frustum Bucket"
        if self.discharge_coeff < 1.0 or self.fluid.name != "Water":
            title += " (Realistic)"
        ax1.set_title(title, fontsize=14, fontweight="bold")

        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(left=0)
        ax1.set_ylim(bottom=0)

        # Add annotations
        total_time = time_points[-1]
        ax1.axhline(y=0, color="r", linestyle="--", alpha=0.5, label="Empty")
        ax1.axhline(y=self.height, color="g", linestyle="--", alpha=0.5, label="Full")
        ax1.legend()

        # Add text box with parameters
        textstr = "Parameters:\n"
        textstr += f"Upper radius (r₁): {self.r1:.3f} m\n"
        textstr += f"Lower radius (r₂): {self.r2:.3f} m\n"
        textstr += f"Volume: {self.volume_liters:.2f} L\n"
        textstr += f"Height: {self.height:.3f} m\n"
        textstr += f"Outlet diameter: {self.outlet_diameter:.4f} m\n"
        textstr += f"Fluid: {self.fluid.name}\n"
        textstr += f"Discharge coeff: {self.discharge_coeff:.2f}\n"
        textstr += f"Total time: {total_time:.2f} s"

        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        ax1.text(
            0.98,
            0.97,
            textstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=props,
            family="monospace",
        )

        # Add derivative plot if requested
        if ax2 is not None:
            dhdt = self.calculate_derivative(time_points, height_points)
            ax2.plot(time_points, dhdt, "r-", linewidth=2)
            ax2.set_xlabel("Time (seconds)", fontsize=12)
            ax2.set_ylabel("Rate of Change (m/s)", fontsize=12)
            ax2.set_title("Drainage Rate (dh/dt)", fontsize=13, fontweight="bold")
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(left=0)
            ax2.axhline(y=0, color="k", linestyle="-", alpha=0.3)

            # Find and annotate max drainage rate
            max_rate_idx = np.argmax(np.abs(dhdt))
            max_rate = dhdt[max_rate_idx]
            max_rate_time = time_points[max_rate_idx]
            ax2.plot(max_rate_time, max_rate, "ro", markersize=8)
            ax2.annotate(
                f"Max rate: {max_rate:.4f} m/s\nat t={max_rate_time:.1f}s",
                xy=(max_rate_time, max_rate),
                xytext=(max_rate_time - total_time * 0.2, max_rate * 0.6),
                arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
                fontsize=9,
                color="red",
            )

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_comparison(
        time_ideal: List[float],
        height_ideal: List[float],
        time_real: List[float],
        height_real: List[float],
        params: dict,
        show_derivative: bool = False,
    ):
        """
        Create a side-by-side comparison plot of ideal vs realistic drainage.

        Args:
            time_ideal: Time points for ideal simulation
            height_ideal: Height points for ideal simulation
            time_real: Time points for realistic simulation
            height_real: Height points for realistic simulation
            params: Dictionary of simulation parameters
            show_derivative: Whether to show rate of change subplots
        """
        if show_derivative:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        else:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            ax3 = ax4 = None  # Initialize to avoid Pylance unbound warning

        # Ideal plot
        ax1.plot(time_ideal, height_ideal, "b-", linewidth=2, label="Ideal")
        ax1.set_xlabel("Time (seconds)", fontsize=12)
        ax1.set_ylabel("Water Height (meters)", fontsize=12)
        ax1.set_title(
            "Ideal Flow (Cd=1.0, No Viscosity)", fontsize=13, fontweight="bold"
        )
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(left=0)
        ax1.set_ylim(bottom=0)
        ax1.axhline(y=0, color="r", linestyle="--", alpha=0.5)
        ax1.axhline(y=params["height"], color="g", linestyle="--", alpha=0.5)

        # Realistic plot
        ax2.plot(time_real, height_real, "r-", linewidth=2, label="Realistic")
        ax2.set_xlabel("Time (seconds)", fontsize=12)
        ax2.set_ylabel("Water Height (meters)", fontsize=12)
        title2 = f"Realistic Flow (Cd={params['discharge_coeff']:.2f},"
        title2 += f" {params['fluid']})"
        ax2.set_title(title2, fontsize=13, fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(left=0)
        ax2.set_ylim(bottom=0)
        ax2.axhline(y=0, color="r", linestyle="--", alpha=0.5)
        ax2.axhline(y=params["height"], color="g", linestyle="--", alpha=0.5)

        # Add parameter info
        textstr = "Parameters:\n"
        textstr += f"r₁: {params['r1']:.3f} m\n"
        textstr += f"r₂: {params['r2']:.3f} m\n"
        textstr += f"Volume: {params['volume']:.1f} L\n"
        textstr += f"Outlet: {params['outlet']:.4f} m\n"
        textstr += f"Height: {params['height']:.3f} m\n\n"
        textstr += f"Ideal time: {time_ideal[-1]:.2f} s\n"
        textstr += f"Real time: {time_real[-1]:.2f} s\n"
        time_diff = (time_real[-1] / time_ideal[-1] - 1) * 100
        textstr += f"Difference: +{time_diff:.1f}%"

        props = dict(boxstyle="round", facecolor="lightyellow", alpha=0.8)
        ax1.text(
            0.98,
            0.97,
            textstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=props,
            family="monospace",
        )

        # Add derivative plots if requested
        if ax3 is not None and ax4 is not None:
            dhdt_ideal = np.gradient(height_ideal, time_ideal)
            dhdt_real = np.gradient(height_real, time_real)

            # Ideal derivative
            ax3.plot(time_ideal, dhdt_ideal, "b-", linewidth=2)
            ax3.set_xlabel("Time (seconds)", fontsize=12)
            ax3.set_ylabel("Rate of Change (m/s)", fontsize=12)
            ax3.set_title("Ideal Drainage Rate (dh/dt)", fontsize=13, fontweight="bold")
            ax3.grid(True, alpha=0.3)
            ax3.set_xlim(left=0)
            ax3.axhline(y=0, color="k", linestyle="-", alpha=0.3)

            # Realistic derivative
            ax4.plot(time_real, dhdt_real, "r-", linewidth=2)
            ax4.set_xlabel("Time (seconds)", fontsize=12)
            ax4.set_ylabel("Rate of Change (m/s)", fontsize=12)
            ax4.set_title(
                "Realistic Drainage Rate (dh/dt)", fontsize=13, fontweight="bold"
            )
            ax4.grid(True, alpha=0.3)
            ax4.set_xlim(left=0)
            ax4.axhline(y=0, color="k", linestyle="-", alpha=0.3)

        plt.tight_layout()
        plt.show()

    def animate_3d_drainage(
        self,
        time_points: List[float],
        height_points: List[float],
        speed_factor: float = 1.0,
    ):
        """
        Create a 3D animated visualization of the bucket draining.

        Args:
            time_points: List of time values (seconds)
            height_points: List of corresponding height values (meters)
            speed_factor: Animation speed multiplier (1.0 = real-time)
        """
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection="3d")

        # Adjust subplot to leave space for title at top
        fig.subplots_adjust(top=0.92)

        # Calculate frames - sample the simulation data
        total_frames = min(len(time_points), 500)  # Limit for performance
        frame_indices = np.linspace(0, len(time_points) - 1, total_frames, dtype=int)

        def create_frustum_surface(r1, r2, height, water_height):
            """Generate frustum bucket mesh."""
            # Vertical resolution
            z = np.linspace(0, height, 50)
            theta = np.linspace(0, 2 * np.pi, 50)

            # Create meshgrid
            Theta, Z = np.meshgrid(theta, z)

            # Radius at each height
            R = r2 + (r1 - r2) * (Z / height)

            # Cartesian coordinates
            X = R * np.cos(Theta)
            Y = R * np.sin(Theta)

            return X, Y, Z

        def create_water_surface(r1, r2, total_height, water_height):
            """Generate water surface mesh."""
            if water_height <= 0:
                return None, None, None

            # Water fills from bottom
            z_water = np.linspace(0, water_height, 30)
            theta = np.linspace(0, 2 * np.pi, 50)

            Theta, Z = np.meshgrid(theta, z_water)
            R = self.r2 + (self.r1 - self.r2) * (Z / total_height)

            X = R * np.cos(Theta)
            Y = R * np.sin(Theta)

            return X, Y, Z

        def create_falling_water(water_height, frame_time):
            """Generate falling water stream from outlet."""
            if water_height <= 0:
                return None, None, None

            # Stream falls from bottom center
            stream_length = 0.3  # meters
            n_particles = 20

            # Vertical positions
            z_stream = np.linspace(-stream_length, 0, n_particles)

            # Slight spread as it falls
            theta = np.linspace(0, 2 * np.pi, 8)
            spread = 0.005  # small radius

            x_stream = spread * np.cos(theta[:, np.newaxis])
            y_stream = spread * np.sin(theta[:, np.newaxis])
            z_stream = np.tile(z_stream, (len(theta), 1))

            return x_stream, y_stream, z_stream

        def init():
            """Initialize the plot."""
            ax.clear()
            ax.set_xlabel("X (meters)", fontsize=10)
            ax.set_ylabel("Y (meters)", fontsize=10)
            ax.set_zlabel("Height (meters)", fontsize=10)
            fig.suptitle(
                "3D Bucket Drainage Visualization", fontsize=13, fontweight="bold"
            )

            # Set consistent axis limits
            max_r = self.r1 * 1.2
            ax.set_xlim(-max_r, max_r)
            ax.set_ylim(-max_r, max_r)
            ax.set_zlim(-0.3, self.height * 1.1)

            # Ground plane
            ground_size = max_r
            xx, yy = np.meshgrid(
                np.linspace(-ground_size, ground_size, 10),
                np.linspace(-ground_size, ground_size, 10),
            )
            zz = np.zeros_like(xx) - 0.3
            ax.plot_surface(xx, yy, zz, alpha=0.2, color="brown")

            return []

        def update(frame):
            """Update animation frame."""
            ax.clear()

            idx = frame_indices[frame]
            current_height = height_points[idx]
            current_time = time_points[idx]

            # Set labels and title with current info
            ax.set_xlabel("X (meters)", fontsize=10)
            ax.set_ylabel("Y (meters)", fontsize=10)
            ax.set_zlabel("Height (meters)", fontsize=10)
            title = f"3D Bucket Drainage - Time: {current_time:.1f}s | "
            title += f"Water Height: {current_height:.3f}m"
            fig.suptitle(title, fontsize=12, fontweight="bold")

            # Set consistent axis limits
            max_r = self.r1 * 1.2
            ax.set_xlim(-max_r, max_r)
            ax.set_ylim(-max_r, max_r)
            ax.set_zlim(-0.3, self.height * 1.1)

            # Ground plane
            ground_size = max_r
            xx, yy = np.meshgrid(
                np.linspace(-ground_size, ground_size, 10),
                np.linspace(-ground_size, ground_size, 10),
            )
            zz = np.zeros_like(xx) - 0.3
            ax.plot_surface(xx, yy, zz, alpha=0.2, color="brown")

            # Draw frustum bucket (semi-transparent)
            X_bucket, Y_bucket, Z_bucket = create_frustum_surface(
                self.r1, self.r2, self.height, current_height
            )
            ax.plot_surface(
                X_bucket,
                Y_bucket,
                Z_bucket,
                alpha=0.15,
                color="gray",
                edgecolor="black",
                linewidth=0.3,
            )

            # Draw water inside bucket
            if current_height > 0.001:
                X_water, Y_water, Z_water = create_water_surface(
                    self.r1, self.r2, self.height, current_height
                )
                if X_water is not None:
                    ax.plot_surface(
                        X_water,
                        Y_water,
                        Z_water,
                        alpha=0.7,
                        color="cyan",
                        edgecolor="blue",
                        linewidth=0.1,
                    )

                # Draw falling water stream
                x_stream, y_stream, z_stream = create_falling_water(
                    current_height, current_time
                )
                if x_stream is not None:
                    ax.plot_surface(
                        x_stream, y_stream, z_stream, alpha=0.6, color="lightblue"
                    )

            # Set viewing angle
            ax.view_init(elev=20, azim=45 + frame * 0.5)  # Slow rotation

            return []

        # Calculate animation interval based on speed factor
        # Target ~30 fps for smooth animation
        total_duration_ms = (time_points[-1] * 1000) / speed_factor
        interval = max(total_duration_ms / total_frames, 33)  # min 33ms (30fps)

        print("\nGenerating 3D animation...")
        print(f"  Total frames: {total_frames}")
        print(f"  Animation speed: {speed_factor}x real-time")
        print(f"  Duration: {total_duration_ms/1000:.1f} seconds")
        print("  (Close the window to continue)\n")

        _ = FuncAnimation(
            fig,
            update,
            frames=total_frames,
            init_func=init,
            interval=interval,
            blit=False,
            repeat=True,
        )

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
                msg = f"Value must be greater than {min_value}. "
                msg += "Please try again."
                print(msg)
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def select_fluid() -> FluidProperties:
    """
    Allow user to select a fluid type from available options.

    Returns:
        Selected FluidProperties
    """
    print("\nAvailable fluids:")
    fluid_list = list(FLUIDS.items())
    for i, (key, fluid) in enumerate(fluid_list, 1):
        if fluid.dynamic_viscosity < 1:
            visc_desc = f"{fluid.dynamic_viscosity*1000:.2f}"
        else:
            visc_desc = f"{fluid.dynamic_viscosity:.1f}"
        print(f"  {i}. {fluid.name:20s} (viscosity: {visc_desc} mPa·s)")

    while True:
        try:
            choice = int(input(f"\nSelect fluid (1-{len(fluid_list)}): "))
            if 1 <= choice <= len(fluid_list):
                return fluid_list[choice - 1][1]
            else:
                print(f"Please enter a number between 1 and {len(fluid_list)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    """Main entry point for the frustum bucket simulator."""
    print("=" * 70)
    print("FRUSTUM BUCKET DRAINAGE SIMULATOR (Real-World Effects)")
    print("=" * 70)
    print("\nThis program simulates fluid draining from a frustum-shaped bucket")
    print("with realistic effects: discharge coefficient and viscosity.\n")

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

    # Select fluid type
    fluid = select_fluid()

    # Get discharge coefficient
    print("\nDischarge coefficient (Cd):")
    print("  • 1.0  = Ideal flow (theoretical)")
    print("  • 0.8  = Smooth, rounded orifice")
    print("  • 0.65 = Typical sharp-edged orifice")
    print("  • 0.6  = Sharp-edged with vena contracta")
    cd = get_float_input("Enter discharge coefficient (0.5-1.0): ")
    if cd > 1.0:
        print("Warning: Cd > 1.0 is non-physical. Using 1.0")
        cd = 1.0
    elif cd < 0.5:
        print("Warning: Cd < 0.5 is very low. Using 0.5")
        cd = 0.5

    # Ask about comparison mode
    print("\nSimulation mode:")
    print("  1. Realistic only")
    print("  2. Side-by-side comparison (Ideal vs Realistic)")
    mode_choice = input("Select mode (1 or 2, default 2): ").strip()
    comparison_mode = mode_choice != "1"

    t = get_float_input("\nTime step t (seconds): ", min_value=0.0)

    # Validate time step
    while t > 1.0:
        print("Warning: Large time step may reduce accuracy.")
        response = input("Continue with this time step? (y/n): ")
        if response.lower() == "y":
            break
        t = get_float_input("Time step t (seconds): ", min_value=0.0)

    # Ask about derivative plotting
    print("\nPlot drainage rate (dh/dt)?")
    print("  This shows the rate of change of water height over time.")
    derivative_choice = (
        input("Show derivative plot? (y/n, default n): ").strip().lower()
    )
    show_derivative = derivative_choice == "y"

    # Ask about 3D animation
    print("\nShow 3D animated visualization?")
    print("  This shows a real-time 3D view of the bucket draining.")
    print("  Warning: Animation may take time to generate.")
    animation_choice = input("Show 3D animation? (y/n, default n): ").strip().lower()
    show_3d_animation = animation_choice == "y"

    animation_speed = 1.0
    if show_3d_animation:
        print("\nAnimation speed:")
        print("  1.0 = Real-time, 2.0 = 2x faster, 0.5 = Half speed")
        speed_input = input("Enter speed factor (default 1.0): ").strip()
        if speed_input:
            try:
                animation_speed = float(speed_input)
                animation_speed = max(0.1, min(animation_speed, 10.0))
            except ValueError:
                print("Invalid input, using default 1.0")
                animation_speed = 1.0

    print("\n" + "=" * 70)
    print("Starting simulation...")
    print("=" * 70 + "\n")

    # Create realistic bucket
    bucket_real = FrustumBucket(r1, r2, volume, d, discharge_coeff=cd, fluid=fluid)

    print("Bucket configuration:")
    print(f"  Calculated height: {bucket_real.height:.4f} m")
    print(f"  Outlet area: {bucket_real.outlet_area:.6f} m²")
    print(f"  Fluid: {fluid.name}")
    print(f"  Discharge coefficient: {cd:.2f}")
    print(f"  Time step: {t} seconds\n")

    if comparison_mode:
        # Run simulations in parallel
        print("Running ideal and realistic simulations in parallel...")
        bucket_ideal = FrustumBucket(
            r1, r2, volume, d, discharge_coeff=1.0, fluid=FLUIDS["water"]
        )

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both simulations to run in parallel
            ideal_future = executor.submit(bucket_ideal.simulate, t)
            real_future = executor.submit(bucket_real.simulate, t)

            # Wait for both to complete and get results
            time_ideal, height_ideal = ideal_future.result()
            time_real, height_real = real_future.result()

        ideal_time = time_ideal[-1]
        real_time = time_real[-1]
        print("Simulations complete!")

        # Display results
        print("\n" + "=" * 70)
        print("RESULTS:")
        print("=" * 70)
        print(f"Ideal drainage time:     {ideal_time:.2f} seconds")
        print(f"Realistic drainage time: {real_time:.2f} seconds")
        time_increase = (real_time / ideal_time - 1) * 100
        print(
            f"Time increase:           +{real_time - ideal_time:.2f} seconds "
            f"({time_increase:.1f}%)"
        )
        print("=" * 70 + "\n")

        # Plot comparison
        print("Generating comparison plot...")
        params = {
            "r1": r1,
            "r2": r2,
            "volume": volume,
            "outlet": d,
            "height": bucket_real.height,
            "discharge_coeff": cd,
            "fluid": fluid.name,
        }
        FrustumBucket.plot_comparison(
            time_ideal,
            height_ideal,
            time_real,
            height_real,
            params,
            show_derivative=show_derivative,
        )

        # Show 3D animation if requested (use realistic simulation)
        if show_3d_animation:
            print("\nGenerating 3D visualization for realistic simulation...")
            bucket_real.animate_3d_drainage(
                time_real, height_real, speed_factor=animation_speed
            )
    else:
        # Run realistic simulation only
        time_points, height_points = bucket_real.simulate(t)
        total_time = time_points[-1]

        print("=" * 70)
        print(f"RESULT: {total_time:.2f} seconds")
        print("=" * 70)
        print(f"\nThe bucket takes {total_time:.2f} seconds to drain with")
        print(f"{fluid.name} and discharge coefficient {cd:.2f}.\n")

        # Plot results
        print("Generating plot...")
        bucket_real.plot_simulation(
            time_points, height_points, show_derivative=show_derivative
        )

        # Show 3D animation if requested
        if show_3d_animation:
            print("\nGenerating 3D visualization...")
            bucket_real.animate_3d_drainage(
                time_points, height_points, speed_factor=animation_speed
            )


if __name__ == "__main__":
    main()
