"""
OpenVSP utility helpers for AeroDemonstrator.

This module provides helper functions to set up and run OpenVSP models
and VSPAero analyses from Python.

Requires the ``openvsp`` package to be installed.
See https://openvsp.org/pyapi_docs/latest/ for the full OpenVSP Python API.

Notes
-----
OpenVSP is an open-source parametric aircraft geometry tool developed by NASA.
The Python API (``openvsp`` package) allows programmatic geometry creation and
aerodynamic analysis through VSPAero.

Installation
------------
Install the OpenVSP Python API with::

    pip install openvsp

or download prebuilt wheels from https://openvsp.org.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

try:
    import openvsp as vsp
    HAS_OPENVSP = True
except ImportError:
    HAS_OPENVSP = False
    vsp = None  # type: ignore[assignment]


def check_openvsp() -> bool:
    """
    Check whether the OpenVSP Python API is available.

    Returns
    -------
    bool
        ``True`` if ``openvsp`` can be imported, ``False`` otherwise.
    """
    return HAS_OPENVSP


def init_vsp(title: str = "AeroDemonstrator") -> None:
    """
    Initialize a fresh OpenVSP model.

    Parameters
    ----------
    title : str, optional
        Title for the VSP model. Default is ``'AeroDemonstrator'``.

    Raises
    ------
    ImportError
        If the ``openvsp`` package is not installed.
    """
    if not HAS_OPENVSP:
        raise ImportError(
            "The 'openvsp' package is not installed. "
            "Install it with: pip install openvsp"
        )
    vsp.ClearVSPModel()
    vsp.Update()


def add_wing(
    span: float = 10.0,
    root_chord: float = 2.0,
    tip_chord: float = 1.0,
    sweep_deg: float = 0.0,
    dihedral_deg: float = 0.0,
    x_offset: float = 0.0,
    z_offset: float = 0.0,
    name: str = "Wing",
) -> Optional[str]:
    """
    Add a trapezoidal wing to the current VSP model.

    Parameters
    ----------
    span : float
        Full wing span [m]. Default 10.0.
    root_chord : float
        Root chord [m]. Default 2.0.
    tip_chord : float
        Tip chord [m]. Default 1.0.
    sweep_deg : float
        Quarter-chord sweep angle [degrees]. Default 0.0.
    dihedral_deg : float
        Dihedral angle [degrees]. Default 0.0.
    x_offset : float
        X-position of wing origin [m]. Default 0.0.
    z_offset : float
        Z-position of wing [m]. Default 0.0.
    name : str
        Geometry name in VSP. Default ``'Wing'``.

    Returns
    -------
    str or None
        VSP geometry ID string, or ``None`` if OpenVSP is unavailable.
    """
    if not HAS_OPENVSP:
        return None

    wing_id = vsp.AddGeom("WING", "")
    vsp.SetGeomName(wing_id, name)

    # Set span (half-span in VSP = full_span/2)
    vsp.SetParmVal(wing_id, "TotalSpan", "WingGeom", float(span))
    vsp.SetParmVal(wing_id, "Root_Chord", "XSec_1", float(root_chord))
    vsp.SetParmVal(wing_id, "Tip_Chord", "XSec_1", float(tip_chord))
    vsp.SetParmVal(wing_id, "Sweep", "XSec_1", float(sweep_deg))
    vsp.SetParmVal(wing_id, "Dihedral", "XSec_1", float(dihedral_deg))

    # Position
    vsp.SetParmVal(wing_id, "X_Rel_Location", "XForm", float(x_offset))
    vsp.SetParmVal(wing_id, "Z_Rel_Location", "XForm", float(z_offset))

    vsp.Update()
    return wing_id


def add_fuselage(
    length: float = 10.0,
    max_diameter: float = 1.5,
    name: str = "Fuselage",
) -> Optional[str]:
    """
    Add a simple fuselage to the current VSP model.

    Parameters
    ----------
    length : float
        Fuselage length [m]. Default 10.0.
    max_diameter : float
        Maximum diameter [m]. Default 1.5.
    name : str
        Geometry name. Default ``'Fuselage'``.

    Returns
    -------
    str or None
        VSP geometry ID, or ``None`` if OpenVSP is unavailable.
    """
    if not HAS_OPENVSP:
        return None

    fuse_id = vsp.AddGeom("FUSELAGE", "")
    vsp.SetGeomName(fuse_id, name)
    vsp.SetParmVal(fuse_id, "Length", "Design", float(length))
    vsp.SetParmVal(fuse_id, "Diameter", "Design", float(max_diameter))
    vsp.Update()
    return fuse_id


def add_horizontal_tail(
    span: float = 4.0,
    root_chord: float = 1.2,
    tip_chord: float = 0.7,
    x_offset: float = 8.5,
    z_offset: float = 0.2,
    name: str = "HTail",
) -> Optional[str]:
    """
    Add a horizontal tail surface.

    Parameters
    ----------
    span : float
        Full horizontal tail span [m]. Default 4.0.
    root_chord : float
        Root chord [m]. Default 1.2.
    tip_chord : float
        Tip chord [m]. Default 0.7.
    x_offset : float
        X-position [m]. Default 8.5.
    z_offset : float
        Z-position [m]. Default 0.2.
    name : str
        Geometry name. Default ``'HTail'``.

    Returns
    -------
    str or None
        VSP geometry ID, or ``None`` if OpenVSP is unavailable.
    """
    return add_wing(
        span=span,
        root_chord=root_chord,
        tip_chord=tip_chord,
        x_offset=x_offset,
        z_offset=z_offset,
        name=name,
    )


def add_vertical_tail(
    height: float = 2.5,
    root_chord: float = 1.5,
    tip_chord: float = 0.8,
    x_offset: float = 8.0,
    z_offset: float = 0.0,
    name: str = "VTail",
) -> Optional[str]:
    """
    Add a vertical tail surface.

    Parameters
    ----------
    height : float
        Vertical tail height [m]. Default 2.5.
    root_chord : float
        Root chord [m]. Default 1.5.
    tip_chord : float
        Tip chord [m]. Default 0.8.
    x_offset : float
        X-position [m]. Default 8.0.
    z_offset : float
        Z-position [m]. Default 0.0.
    name : str
        Geometry name. Default ``'VTail'``.

    Returns
    -------
    str or None
        VSP geometry ID, or ``None`` if OpenVSP is unavailable.
    """
    if not HAS_OPENVSP:
        return None

    vtail_id = vsp.AddGeom("WING", "")
    vsp.SetGeomName(vtail_id, name)
    vsp.SetParmVal(vtail_id, "TotalSpan", "WingGeom", float(height))
    vsp.SetParmVal(vtail_id, "Root_Chord", "XSec_1", float(root_chord))
    vsp.SetParmVal(vtail_id, "Tip_Chord", "XSec_1", float(tip_chord))
    vsp.SetParmVal(vtail_id, "X_Rel_Location", "XForm", float(x_offset))
    vsp.SetParmVal(vtail_id, "Z_Rel_Location", "XForm", float(z_offset))
    # Rotate 90 degrees about X to make it vertical
    vsp.SetParmVal(vtail_id, "X_Rel_Rotation", "XForm", 90.0)
    vsp.Update()
    return vtail_id


def run_vspaero(
    alpha_start: float = 0.0,
    alpha_end: float = 10.0,
    alpha_npts: int = 5,
    mach: float = 0.1,
    ref_area: float = 1.0,
    ref_span: float = 1.0,
    ref_chord: float = 1.0,
    analysis_type: str = "VLM",
) -> Optional[dict]:
    """
    Run a VSPAero analysis sweep on the current model.

    Parameters
    ----------
    alpha_start : float
        Start angle of attack [degrees]. Default 0.0.
    alpha_end : float
        End angle of attack [degrees]. Default 10.0.
    alpha_npts : int
        Number of alpha points. Default 5.
    mach : float
        Mach number. Default 0.1 (incompressible).
    ref_area : float
        Reference area [m^2]. Default 1.0.
    ref_span : float
        Reference span [m]. Default 1.0.
    ref_chord : float
        Reference chord [m]. Default 1.0.
    analysis_type : str
        ``'VLM'`` for Vortex Lattice Method or ``'Panel'`` for panel method.
        Default ``'VLM'``.

    Returns
    -------
    dict or None
        Dictionary with VSPAero result arrays, or ``None`` if OpenVSP is
        unavailable.

    Notes
    -----
    The returned dictionary contains::

        {
            "Alpha": array of alpha values,
            "CL":    array of lift coefficients,
            "CDi":   array of induced drag coefficients,
            "CY":    array of side force coefficients,
            "Cl":    array of rolling moment coefficients,
            "Cm":    array of pitching moment coefficients,
            "Cn":    array of yawing moment coefficients,
        }
    """
    if not HAS_OPENVSP:
        return None

    analysis_name = "VSPAEROSweep"
    vsp.SetAnalysisInputDefaults(analysis_name)

    # Analysis method: 0=VLM, 1=Panel
    method = 0 if analysis_type.upper() == "VLM" else 1
    vsp.SetIntAnalysisInput(analysis_name, "AnalysisMethod", [method])

    # Alpha sweep
    vsp.SetDoubleAnalysisInput(analysis_name, "AlphaStart", [alpha_start])
    vsp.SetDoubleAnalysisInput(analysis_name, "AlphaEnd", [alpha_end])
    vsp.SetIntAnalysisInput(analysis_name, "AlphaNpts", [alpha_npts])

    # Reference values
    vsp.SetDoubleAnalysisInput(analysis_name, "Mach", [mach])
    vsp.SetDoubleAnalysisInput(analysis_name, "Sref", [ref_area])
    vsp.SetDoubleAnalysisInput(analysis_name, "bref", [ref_span])
    vsp.SetDoubleAnalysisInput(analysis_name, "cref", [ref_chord])

    # Execute the analysis
    results_id = vsp.ExecAnalysis(analysis_name)

    # Extract results
    alpha_res = list(vsp.GetDoubleResults(results_id, "Alpha"))
    cl_res = list(vsp.GetDoubleResults(results_id, "CL"))
    cdi_res = list(vsp.GetDoubleResults(results_id, "CDi"))

    result = {
        "Alpha": alpha_res,
        "CL": cl_res,
        "CDi": cdi_res,
    }

    for key in ["CY", "Cl", "Cm", "Cn"]:
        try:
            result[key] = list(vsp.GetDoubleResults(results_id, key))
        except Exception:
            result[key] = [0.0] * len(alpha_res)

    return result


def save_vsp3_file(filepath: str) -> None:
    """
    Save the current VSP model to a .vsp3 file.

    Parameters
    ----------
    filepath : str
        Output file path (should end in ``.vsp3``).

    Raises
    ------
    ImportError
        If the ``openvsp`` package is not installed.
    """
    if not HAS_OPENVSP:
        raise ImportError("The 'openvsp' package is not installed.")
    vsp.WriteVSPFile(str(filepath))


def load_vsp3_file(filepath: str) -> None:
    """
    Load a VSP model from a .vsp3 file.

    Parameters
    ----------
    filepath : str
        Input ``.vsp3`` file path.

    Raises
    ------
    ImportError
        If the ``openvsp`` package is not installed.
    FileNotFoundError
        If the specified file does not exist.
    """
    if not HAS_OPENVSP:
        raise ImportError("The 'openvsp' package is not installed.")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"VSP file not found: {filepath}")
    vsp.ReadVSPFile(str(filepath))
    vsp.Update()
