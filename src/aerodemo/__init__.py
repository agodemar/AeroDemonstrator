"""
AeroDemonstrator - A collection of aerodynamic demonstrations.

This package provides utility classes and functions for demonstrating
aerodynamic features of airfoils, finite wings, and aircraft configurations.
"""

from .naca_airfoil import NACAFourDigit, NACAFiveDigit
from .vlm import VortexLatticeMethod

__all__ = ["NACAFourDigit", "NACAFiveDigit", "VortexLatticeMethod"]
__version__ = "0.1.0"
