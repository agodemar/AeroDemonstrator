"""
NACA airfoil geometry generators.

This module provides classes for generating NACA 4-digit and 5-digit airfoil
coordinates and computing basic aerodynamic properties.

References
----------
Abbott, I.H., and Von Doenhoff, A.E., "Theory of Wing Sections",
Dover Publications, 1959.
"""

import numpy as np


class NACAFourDigit:
    """
    NACA 4-digit airfoil geometry generator.

    The NACA 4-digit series airfoils are defined by:
    - First digit: maximum camber as a percentage of chord
    - Second digit: location of maximum camber in tenths of chord
    - Last two digits: maximum thickness as a percentage of chord

    Parameters
    ----------
    designation : str
        NACA 4-digit designation, e.g. '2412', '0012', '4415'.
    n_points : int, optional
        Number of points on each surface (upper/lower). Default is 100.
    cosine_spacing : bool, optional
        Use cosine spacing for denser distribution near leading/trailing edges.
        Default is True.

    Examples
    --------
    >>> airfoil = NACAFourDigit('2412')
    >>> x_upper, y_upper, x_lower, y_lower = airfoil.coordinates()
    """

    def __init__(self, designation: str, n_points: int = 100, cosine_spacing: bool = True):
        if len(designation) != 4 or not designation.isdigit():
            raise ValueError(f"Invalid NACA 4-digit designation: '{designation}'")
        self.designation = designation
        self.n_points = n_points
        self.cosine_spacing = cosine_spacing

        m = int(designation[0]) / 100.0   # max camber fraction of chord
        p = int(designation[1]) / 10.0    # location of max camber (fraction of chord)
        t = int(designation[2:]) / 100.0  # max thickness fraction of chord

        self.m = m
        self.p = p
        self.t = t

    @property
    def max_camber(self) -> float:
        """Maximum camber as fraction of chord."""
        return self.m

    @property
    def max_camber_location(self) -> float:
        """Location of maximum camber as fraction of chord."""
        return self.p

    @property
    def max_thickness(self) -> float:
        """Maximum thickness as fraction of chord."""
        return self.t

    def _x_coords(self) -> np.ndarray:
        """Generate x-coordinates with optional cosine spacing."""
        if self.cosine_spacing:
            beta = np.linspace(0, np.pi, self.n_points)
            return 0.5 * (1 - np.cos(beta))
        else:
            return np.linspace(0, 1, self.n_points)

    def thickness(self, x: np.ndarray) -> np.ndarray:
        """
        Compute half-thickness distribution.

        Parameters
        ----------
        x : array_like
            Chordwise positions (0 to 1).

        Returns
        -------
        yt : ndarray
            Half-thickness values.
        """
        t = self.t
        yt = (t / 0.2) * (
            0.2969 * np.sqrt(x)
            - 0.1260 * x
            - 0.3516 * x**2
            + 0.2843 * x**3
            - 0.1015 * x**4
        )
        return yt

    def camber_line(self, x: np.ndarray):
        """
        Compute camber line and its gradient.

        Parameters
        ----------
        x : array_like
            Chordwise positions (0 to 1).

        Returns
        -------
        yc : ndarray
            Camber line ordinates.
        dyc_dx : ndarray
            Gradient of the camber line.
        """
        m, p = self.m, self.p
        yc = np.where(
            x < p,
            m / p**2 * (2 * p * x - x**2) if p > 0 else np.zeros_like(x),
            m / (1 - p) ** 2 * (1 - 2 * p + 2 * p * x - x**2) if p > 0 else np.zeros_like(x),
        )
        if p > 0:
            dyc_dx = np.where(
                x < p,
                2 * m / p**2 * (p - x),
                2 * m / (1 - p) ** 2 * (p - x),
            )
        else:
            dyc_dx = np.zeros_like(x)
        return yc, dyc_dx

    def coordinates(self):
        """
        Compute upper and lower surface coordinates.

        Returns
        -------
        x_upper : ndarray
        y_upper : ndarray
        x_lower : ndarray
        y_lower : ndarray
        """
        x = self._x_coords()
        yt = self.thickness(x)
        yc, dyc_dx = self.camber_line(x)
        theta = np.arctan(dyc_dx)

        x_upper = x - yt * np.sin(theta)
        y_upper = yc + yt * np.cos(theta)
        x_lower = x + yt * np.sin(theta)
        y_lower = yc - yt * np.cos(theta)

        return x_upper, y_upper, x_lower, y_lower

    def lift_curve_slope(self) -> float:
        """
        Thin-airfoil theory lift-curve slope (per radian).

        Returns
        -------
        float
            dCL/dalpha = 2*pi rad^{-1}
        """
        return 2 * np.pi

    def zero_lift_angle(self) -> float:
        """
        Zero-lift angle of attack (radians) from thin-airfoil theory.

        Returns
        -------
        float
            alpha_L0 in radians.
        """
        if self.p == 0 or self.m == 0:
            return 0.0
        m, p = self.m, self.p
        # Thin-airfoil result for NACA 4-digit; p is in (0, 1] by construction
        # Use log1p for numerical stability: log(1-p) = log1p(-p)
        alpha_L0 = -m / p**2 * (
            0.5 * p**2 - p + (1 - p) * np.log1p(-p) + p * np.log(p) + 0.5
        )
        return float(alpha_L0)

    def cl(self, alpha_deg: float) -> float:
        """
        Lift coefficient from thin-airfoil theory.

        Parameters
        ----------
        alpha_deg : float
            Angle of attack in degrees.

        Returns
        -------
        float
            Lift coefficient.
        """
        alpha = np.deg2rad(alpha_deg)
        return self.lift_curve_slope() * (alpha - self.zero_lift_angle())

    def __repr__(self) -> str:
        return (
            f"NACAFourDigit('{self.designation}', "
            f"m={self.m:.4f}, p={self.p:.2f}, t={self.t:.4f})"
        )


class NACAFiveDigit:
    """
    NACA 5-digit airfoil geometry generator.

    The NACA 5-digit series airfoils provide reflex camber options.
    Designation examples: '23012', '23015', '23112' (reflex).

    Parameters
    ----------
    designation : str
        NACA 5-digit designation, e.g. '23012'.
    n_points : int, optional
        Number of surface points. Default is 100.
    cosine_spacing : bool, optional
        Use cosine spacing. Default is True.

    Examples
    --------
    >>> airfoil = NACAFiveDigit('23012')
    >>> x_u, y_u, x_l, y_l = airfoil.coordinates()
    """

    _CAMBER_PARAMS = {
        210: (0.0580, 0.1260, 0.4300),
        220: (0.1260, 0.2025, 0.6500),
        230: (0.2025, 0.2900, 0.7700),  # most common
        240: (0.2900, 0.3910, 0.8300),
        250: (0.3910, 0.4800, 0.8600),
    }

    def __init__(self, designation: str, n_points: int = 100, cosine_spacing: bool = True):
        if len(designation) != 5 or not designation.isdigit():
            raise ValueError(f"Invalid NACA 5-digit designation: '{designation}'")
        self.designation = designation
        self.n_points = n_points
        self.cosine_spacing = cosine_spacing

        cl_design = int(designation[0]) * 3 / 20.0  # design lift coefficient
        p_raw = int(designation[1]) * 5          # position index (10, 15, 20...)
        reflex = int(designation[2])              # 0=normal, 1=reflex
        t = int(designation[3:]) / 100.0         # thickness

        self.cl_design = cl_design
        self.p_raw = p_raw
        self.reflex = reflex == 1
        self.t = t

        key = int(designation[0]) * 100 + int(designation[1]) * 10
        if key not in self._CAMBER_PARAMS:
            raise ValueError(
                f"Unsupported 5-digit camber code '{designation[:3]}'. "
                f"Supported codes: {list(self._CAMBER_PARAMS.keys())}"
            )
        # k1 and p from lookup tables (Abbott & Von Doenhoff, Table 5)
        _k1_table = {210: 361.4, 220: 51.64, 230: 15.957, 240: 6.643, 250: 3.230}
        self._k1 = _k1_table[key]
        self._p_c = self._CAMBER_PARAMS[key][1]

    @property
    def max_thickness(self) -> float:
        return self.t

    def _x_coords(self) -> np.ndarray:
        if self.cosine_spacing:
            beta = np.linspace(0, np.pi, self.n_points)
            return 0.5 * (1 - np.cos(beta))
        return np.linspace(0, 1, self.n_points)

    def thickness(self, x: np.ndarray) -> np.ndarray:
        t = self.t
        return (t / 0.2) * (
            0.2969 * np.sqrt(x)
            - 0.1260 * x
            - 0.3516 * x**2
            + 0.2843 * x**3
            - 0.1015 * x**4
        )

    def camber_line(self, x: np.ndarray):
        k1 = self._k1
        p = self._p_c
        yc = np.where(
            x <= p,
            k1 / 6.0 * (x**3 - 3 * p * x**2 + p**2 * (3 - p) * x),
            k1 * p**3 / 6.0 * (1 - x),
        )
        dyc_dx = np.where(
            x <= p,
            k1 / 6.0 * (3 * x**2 - 6 * p * x + p**2 * (3 - p)),
            -k1 * p**3 / 6.0 * np.ones_like(x),
        )
        return yc, dyc_dx

    def coordinates(self):
        x = self._x_coords()
        yt = self.thickness(x)
        yc, dyc_dx = self.camber_line(x)
        theta = np.arctan(dyc_dx)

        x_upper = x - yt * np.sin(theta)
        y_upper = yc + yt * np.cos(theta)
        x_lower = x + yt * np.sin(theta)
        y_lower = yc - yt * np.cos(theta)

        return x_upper, y_upper, x_lower, y_lower

    def __repr__(self) -> str:
        return f"NACAFiveDigit('{self.designation}', t={self.t:.4f})"
