"""Tests for NACA airfoil geometry generation."""

import numpy as np
import pytest
from aerodemo.naca_airfoil import NACAFourDigit, NACAFiveDigit


class TestNACAFourDigit:
    def test_symmetric_airfoil_coordinates(self):
        af = NACAFourDigit("0012")
        xu, yu, xl, yl = af.coordinates()
        # Symmetric: upper and lower should be mirror images
        np.testing.assert_allclose(yu, -yl, atol=1e-10)
        np.testing.assert_allclose(xu, xl, atol=1e-10)

    def test_cambered_airfoil_2412(self):
        af = NACAFourDigit("2412")
        assert af.m == pytest.approx(0.02)
        assert af.p == pytest.approx(0.4)
        assert af.t == pytest.approx(0.12)

    def test_invalid_designation(self):
        with pytest.raises(ValueError):
            NACAFourDigit("ABC1")
        with pytest.raises(ValueError):
            NACAFourDigit("12345")

    def test_lift_curve_slope(self):
        af = NACAFourDigit("0012")
        assert af.lift_curve_slope() == pytest.approx(2 * np.pi, rel=1e-6)

    def test_zero_lift_angle_symmetric(self):
        af = NACAFourDigit("0012")
        assert af.zero_lift_angle() == pytest.approx(0.0, abs=1e-10)

    def test_cl_at_zero_alpha(self):
        af = NACAFourDigit("0012")
        assert af.cl(0.0) == pytest.approx(0.0, abs=1e-10)

    def test_cl_positive_alpha(self):
        af = NACAFourDigit("0012")
        assert af.cl(5.0) > 0.0

    def test_coordinate_count(self):
        af = NACAFourDigit("2412", n_points=50)
        xu, yu, xl, yl = af.coordinates()
        assert len(xu) == 50
        assert len(yu) == 50

    def test_thickness_distribution(self):
        af = NACAFourDigit("0012")
        x = np.array([0.0, 0.3, 1.0])
        yt = af.thickness(x)
        # Max thickness at x~0.3 should be positive
        assert yt[1] > 0.0
        # At trailing edge, thickness approaches zero
        assert yt[2] == pytest.approx(0.00126, abs=1e-4)


class TestNACAFiveDigit:
    def test_23012_designation(self):
        af = NACAFiveDigit("23012")
        assert af.t == pytest.approx(0.12)

    def test_invalid_designation(self):
        with pytest.raises(ValueError):
            NACAFiveDigit("ABCDE")
        with pytest.raises(ValueError):
            NACAFiveDigit("1234")

    def test_coordinate_shapes(self):
        af = NACAFiveDigit("23012")
        xu, yu, xl, yl = af.coordinates()
        assert xu.shape == yu.shape == xl.shape == yl.shape
        assert len(xu) == 100
