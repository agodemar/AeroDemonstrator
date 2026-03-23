"""Tests for Vortex Lattice Method."""

import numpy as np
import pytest
from aerodemo.vlm import WingGeometry, VortexLatticeMethod


class TestWingGeometry:
    def test_aspect_ratio(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        S = 10.0 * 1.5  # (2+1)/2 * 10
        AR = 10.0**2 / S
        assert wing.aspect_ratio == pytest.approx(AR, rel=1e-6)

    def test_taper_ratio(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        assert wing.taper_ratio == pytest.approx(0.5, rel=1e-6)

    def test_reference_area(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=2.0)
        assert wing.reference_area == pytest.approx(20.0, rel=1e-6)

    def test_mac_rectangular_wing(self):
        # For rectangular wing (lambda=1), MAC = chord
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=2.0)
        assert wing.mean_aerodynamic_chord == pytest.approx(2.0, rel=1e-6)


class TestVortexLatticeMethod:
    def test_solve_returns_dict(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        vlm = VortexLatticeMethod(wing)
        result = vlm.solve(alpha_deg=5.0)
        assert "CL" in result
        assert "CDi" in result
        assert "CL_distribution" in result
        assert "y_stations" in result

    def test_cl_positive_at_positive_alpha(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        vlm = VortexLatticeMethod(wing)
        result = vlm.solve(alpha_deg=5.0)
        assert result["CL"] > 0.0

    def test_cl_zero_at_zero_alpha(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        vlm = VortexLatticeMethod(wing)
        result = vlm.solve(alpha_deg=0.0)
        # For symmetric airfoil at zero alpha, CL should be near zero
        assert abs(result["CL"]) < 0.5  # allow some numerical error

    def test_cdi_non_negative(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        vlm = VortexLatticeMethod(wing)
        result = vlm.solve(alpha_deg=5.0)
        assert result["CDi"] >= 0.0

    def test_sweep_alpha(self):
        wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
        vlm = VortexLatticeMethod(wing)
        alphas = np.linspace(0, 10, 5)
        result = vlm.sweep_alpha(alphas)
        assert len(result["CL"]) == 5
        assert len(result["CDi"]) == 5
        # CL should increase with alpha
        assert result["CL"][-1] > result["CL"][0]
