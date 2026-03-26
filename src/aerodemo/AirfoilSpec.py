from __future__ import annotations

from typing import Optional, Dict
from dataclasses import dataclass, field
from _vsppytools_bootstrap import import_openvsp_from_local_vsppytools

vsp = import_openvsp_from_local_vsppytools()

@dataclass
class AirfoilSpec:
    """
    Airfoil definition for one spanwise station (root, break, tip, ...).

    Supported kinds:
        "naca4"
            OpenVSP 4-series airfoil.

        "file"
            Airfoil loaded from file through ReadFileAirfoil(...) from OpenVSP API.

        "custom"
            Any OpenVSP XSec airfoil type, driven by xsec_type + extra_parms.

    Defaults:
        kind = "naca4"
            Default station airfoil is a 4-series airfoil.

        thickness = 0.12
            Thickness/chord ratio. For the default settings with zero camber,
            this corresponds to a NACA 0012-like section.

        camber = 0.0
            Maximum camber (4-series only).

        camber_loc = 0.4
            Location of maximum camber (4-series only).

        sharp_te = True
            Use a sharp trailing edge when supported.

        file_path = None
            Path to the airfoil file when kind == "file".

        xsec_type = None
            OpenVSP XSec type enum when kind == "custom".

        extra_parms = {}
            Additional OpenVSP XSecCurve parameters for custom airfoils.
            Example:
                {"Series": 63, "IdealCl": 0.3, "A": 1.0, "ThickChord": 0.12}
    """
    kind: str = "naca4"
    thickness: float = 0.12
    camber: float = 0.0
    camber_loc: float = 0.4
    sharp_te: bool = True
    file_path: Optional[str] = None
    xsec_type: Optional[int] = None
    extra_parms: Dict[str, float] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            "AirfoilSpec:\n"
            f"  kind: {self.kind}\n"
            f"  thickness: {self.thickness:.3f} (-)\n"
            f"  camber: {self.camber:.3f} (-)\n"
            f"  camber_loc: {self.camber_loc:.3f} x/c\n"
            f"  sharp_te: {self.sharp_te}\n"
            f"  file_path: {self.file_path}\n"
            f"  xsec_type: {self.xsec_type}\n"
            f"  extra_parms: {self.extra_parms}"
        )


# ----------------------------------------------------------------------
# Example usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example: a 4-series section similar to a NACA 2412 station.
    airfoil = AirfoilSpec(
        kind="naca4",
        thickness=0.12,
        camber=0.02,
        camber_loc=0.4,
        sharp_te=True,
    )

    print(airfoil)