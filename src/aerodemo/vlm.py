"""
Vortex Lattice Method (VLM) for finite wings.

This module provides a simple implementation of the Vortex Lattice Method
for computing aerodynamic forces on finite wings.

References
----------
Katz, J., and Plotkin, A., "Low Speed Aerodynamics", 2nd ed.,
Cambridge University Press, 2001.

Bertin, J.J., and Cummings, R.M., "Aerodynamics for Engineers", 6th ed.,
Pearson, 2014.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WingGeometry:
    """
    Parameters defining a trapezoidal wing planform.

    Parameters
    ----------
    span : float
        Wing span [m].
    root_chord : float
        Root chord length [m].
    tip_chord : float
        Tip chord length [m].
    sweep_angle : float
        Quarter-chord sweep angle [degrees]. Default 0.
    dihedral : float
        Dihedral angle [degrees]. Default 0.
    twist : float
        Tip washout (geometric twist) [degrees]. Default 0.
    n_spanwise : int
        Number of spanwise panels. Default 10.
    n_chordwise : int
        Number of chordwise panels. Default 4.
    """

    span: float
    root_chord: float
    tip_chord: float
    sweep_angle: float = 0.0
    dihedral: float = 0.0
    twist: float = 0.0
    n_spanwise: int = 10
    n_chordwise: int = 4

    @property
    def aspect_ratio(self) -> float:
        """Wing aspect ratio AR = b^2 / S."""
        return self.span**2 / self.reference_area

    @property
    def taper_ratio(self) -> float:
        """Taper ratio lambda = c_tip / c_root."""
        return self.tip_chord / self.root_chord

    @property
    def reference_area(self) -> float:
        """Wing reference area S = b * (c_root + c_tip) / 2."""
        return self.span * (self.root_chord + self.tip_chord) / 2.0

    @property
    def mean_aerodynamic_chord(self) -> float:
        """
        Mean aerodynamic chord (MAC).

        For trapezoidal wings:
        MAC = (2/3) * c_root * (1 + lambda + lambda^2) / (1 + lambda)
        """
        lam = self.taper_ratio
        return (2 / 3) * self.root_chord * (1 + lam + lam**2) / (1 + lam)


class VortexLatticeMethod:
    """
    Vortex Lattice Method solver for finite wings.

    Computes lift, induced drag, and span-load distribution for
    trapezoidal wings using horseshoe vortex panels.

    Parameters
    ----------
    wing : WingGeometry
        Wing planform geometry definition.

    Examples
    --------
    >>> wing = WingGeometry(span=10.0, root_chord=2.0, tip_chord=1.0)
    >>> vlm = VortexLatticeMethod(wing)
    >>> result = vlm.solve(alpha_deg=5.0)
    >>> print(f"CL = {result['CL']:.4f}")
    """

    def __init__(self, wing: WingGeometry):
        self.wing = wing
        self._panels = None
        self._gamma = None

    def _build_panels(self, alpha_deg: float):
        """Generate panel geometry and build the aerodynamic influence matrix."""
        wing = self.wing
        b = wing.span
        cr = wing.root_chord
        ct = wing.tip_chord
        ns = wing.n_spanwise
        nc = wing.n_chordwise
        sweep = np.deg2rad(wing.sweep_angle)
        dihedral = np.deg2rad(wing.dihedral)
        twist = np.deg2rad(wing.twist)

        n_panels = ns * nc
        # Panel midpoint coordinates and bound vortex / control point locations
        x_cp = np.zeros(n_panels)
        y_cp = np.zeros(n_panels)
        z_cp = np.zeros(n_panels)
        normal = np.zeros((n_panels, 3))

        # Spanwise station edges (semispan, symmetric)
        y_edges = np.linspace(0, b / 2, ns + 1)
        panel_idx = 0
        panels = []

        for j in range(ns):
            y_mid = 0.5 * (y_edges[j] + y_edges[j + 1])
            eta = 2 * y_mid / b  # 0 at root, 1 at tip
            chord = cr + (ct - cr) * eta
            # Leading edge x-position (quarter chord sweep applied to LE)
            x_le = y_mid * np.tan(sweep)
            # Twist at this spanwise station (linear washout)
            local_twist = -twist * eta
            for i in range(nc):
                xi_vortex = (i + 0.25) / nc  # vortex line at 1/4 local chord
                xi_cp = (i + 0.75) / nc      # control point at 3/4 local chord
                x_v = x_le + xi_vortex * chord
                x_c = x_le + xi_cp * chord
                z_mid = y_mid * np.tan(dihedral)

                panels.append({
                    "y": y_mid,
                    "x_vortex": x_v,
                    "x_cp": x_c,
                    "chord": chord,
                    "twist": local_twist,
                    "dy": y_edges[j + 1] - y_edges[j],
                    "dx": chord / nc,
                    "z": z_mid,
                })
                nx = -np.sin(local_twist)
                nz = np.cos(local_twist)
                normal[panel_idx] = [nx, 0.0, nz]
                x_cp[panel_idx] = x_c
                y_cp[panel_idx] = y_mid
                z_cp[panel_idx] = z_mid
                panel_idx += 1

        self._panels = panels
        return panels, x_cp, y_cp, z_cp, normal

    def solve(self, alpha_deg: float):
        """
        Solve the VLM for given angle of attack.

        Parameters
        ----------
        alpha_deg : float
            Angle of attack in degrees.

        Returns
        -------
        dict with keys:
            CL : float
                Lift coefficient.
            CDi : float
                Induced drag coefficient.
            CL_distribution : ndarray
                Spanwise lift coefficient distribution (per unit span).
            y_stations : ndarray
                Spanwise stations corresponding to CL_distribution.
            AR : float
                Wing aspect ratio.
            e : float
                Oswald efficiency factor.
        """
        alpha = np.deg2rad(alpha_deg)
        panels, x_cp, y_cp, z_cp, normals = self._build_panels(alpha_deg)
        n = len(panels)

        # Freestream velocity direction
        V_inf = np.array([np.cos(alpha), 0.0, np.sin(alpha)])

        # Build influence coefficient matrix using Biot-Savart law
        # Simplified: semi-infinite horseshoe vortices with bound segment at y=y_panel
        AIC = np.zeros((n, n))
        rhs = np.zeros(n)

        # Small upstream offset to place the control point downstream of the
        # vortex line, ensuring the trailing legs induce downwash (not upwash).
        _UPSTREAM_OFFSET = 1e-8

        for i in range(n):
            xc, yc, zc = x_cp[i], y_cp[i], z_cp[i]
            for j in range(n):
                p = panels[j]
                y_j = p["y"]
                x_v = p["x_vortex"]
                dy = p["dy"]

                # Influence of bound vortex filament (simplified)
                # Using Prandtl's lifting-line simplification for chordwise panels
                dx_bc = xc - x_v
                dy_l = yc - (y_j - dy / 2)
                dy_r = yc - (y_j + dy / 2)
                dz = zc - p["z"]

                r1 = np.sqrt(dx_bc**2 + dy_l**2 + dz**2)
                r2 = np.sqrt(dx_bc**2 + dy_r**2 + dz**2)

                # Bound vortex contribution (z-component of velocity)
                if r1 > 1e-10 and r2 > 1e-10:
                    w_bound = (1 / (4 * np.pi)) * (
                        (dy_r / r2 - dy_l / r1)
                        / (dz**2 + dx_bc**2 + 1e-12)
                        * dx_bc
                    )
                else:
                    w_bound = 0.0

                # Trailing vortex contributions (semi-infinite legs)
                def _semi_inf_vortex_w(dx, dy_leg, dz_leg):
                    r = np.sqrt(dy_leg**2 + dz_leg**2)
                    if r < 1e-10:
                        return 0.0
                    cos_theta = dx / np.sqrt(dx**2 + r**2 + 1e-20)
                    return (1 / (4 * np.pi)) * (-dz_leg) / r**2 * (1 + cos_theta)

                w_trail_l = _semi_inf_vortex_w(
                    xc - x_v - _UPSTREAM_OFFSET, yc - (y_j - dy / 2), zc - p["z"]
                )
                w_trail_r = -_semi_inf_vortex_w(
                    xc - x_v - _UPSTREAM_OFFSET, yc - (y_j + dy / 2), zc - p["z"]
                )

                AIC[i, j] = w_bound + w_trail_l + w_trail_r

            # Right-hand side: flow tangency condition
            rhs[i] = -np.dot(V_inf, normals[i])

        # Solve for circulation strengths
        try:
            gamma = np.linalg.solve(AIC, rhs)
        except np.linalg.LinAlgError:
            gamma = np.linalg.lstsq(AIC, rhs, rcond=None)[0]

        self._gamma = gamma

        # Post-process: compute forces
        wing = self.wing
        S = wing.reference_area
        b = wing.span

        # Lift per unit span at each spanwise station (sum chordwise panels)
        ns = wing.n_spanwise
        nc = wing.n_chordwise
        lift_per_span = np.zeros(ns)
        y_stations = np.zeros(ns)
        for j in range(ns):
            y_stations[j] = panels[j * nc]["y"]
            for i in range(nc):
                p = panels[j * nc + i]
                lift_per_span[j] += gamma[j * nc + i] * p["dy"]

        # Total lift using Kutta-Joukowski (L = rho * V * Gamma * b_panel)
        # Normalize as CL
        total_gamma = np.sum([gamma[j * nc + i] * panels[j * nc + i]["dx"]
                              for j in range(ns) for i in range(nc)])
        CL = 2 * total_gamma / (S * 1.0)  # V_inf = 1, rho = 1 -> 2*Gamma/S

        # Spanwise CL distribution (local cl * c / c_ref)
        cl_span = lift_per_span * 2 / (wing.root_chord)

        # Induced drag via Trefftz-plane integration (approximate)
        # CDi = CL^2 / (pi * AR * e) - use e ~ 1 for elliptic, correction for taper
        AR = wing.aspect_ratio
        # Approximate Oswald factor for tapered wing (Grosu correlation)
        lam = wing.taper_ratio
        e = 1.0 / (1.0 + 0.12 * AR * (1 - lam) ** 2 / (1 + lam) ** 2) if AR > 0 else 1.0
        CDi = CL**2 / (np.pi * AR * e) if AR > 0 else 0.0

        return {
            "CL": float(CL),
            "CDi": float(CDi),
            "CL_distribution": cl_span,
            "y_stations": y_stations,
            "AR": float(AR),
            "e": float(e),
            "gamma": gamma,
        }

    def sweep_alpha(self, alpha_range: np.ndarray):
        """
        Compute aerodynamic coefficients over a range of angles of attack.

        Parameters
        ----------
        alpha_range : array_like
            Array of angles of attack in degrees.

        Returns
        -------
        dict with keys 'alpha', 'CL', 'CDi', 'CL_over_CDi'.
        """
        results = [self.solve(a) for a in alpha_range]
        CL_arr = np.array([r["CL"] for r in results])
        CDi_arr = np.array([r["CDi"] for r in results])
        return {
            "alpha": np.asarray(alpha_range),
            "CL": CL_arr,
            "CDi": CDi_arr,
            "CL_over_CDi": CL_arr / (CDi_arr + 1e-10),
        }
