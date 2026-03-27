from __future__ import annotations

from dataclasses import dataclass
from _vsppytools_bootstrap import import_openvsp_from_local_vsppytools

vsp = import_openvsp_from_local_vsppytools()


@dataclass
class WingSegment:
    """
    One wing panel (one OpenVSP wing section).

    Defaults:
        span = 5.0
            Semi-span of this panel on ONE side of the aircraft.
            With mirrored symmetry enabled, the full airplane span is doubled.

        root_chord = 1.5
            Root chord of the panel.

        tip_chord = 1.0
            Tip chord of the panel.

        sweep_deg = 0.0
            Quarter-chord sweep angle of the panel in degrees.

        dihedral_deg = 0.0
            Dihedral angle of the panel in degrees.

        twist_deg = 0.0
            Twist angle of the panel in degrees.

        sweep_ref_loc = 0.25
            Sweep reference location along the chord.
            0.25 means quarter-chord sweep, per panel.

        twist_ref_loc = 0.25
            Twist reference location along the chord.
            0.25 means twist about the quarter-chord.

        num_U = 5
            Number of spanwise tessellation panels for this section
            (OpenVSP parameter `SectTess_U`).

        cluster_root = 1.0
            Root-side clustering factor for this section
            (OpenVSP parameter `InCluster`).
            1.0 gives near-uniform spacing.

        cluster_tip = 1.0
            Tip-side clustering factor for this section
            (OpenVSP parameter `OutCluster`).
            1.0 gives near-uniform spacing.
    """
    id: str = "WS1"
    
    # Geometry
    span: float = 5.0
    root_chord: float = 1.5
    tip_chord: float = 1.0
    sweep_deg: float = 0.0
    dihedral_deg: float = 0.0
    twist_deg: float = 0.0
    sweep_ref_loc: float = 0.25
    twist_ref_loc: float = 0.25

    # Discretization
    num_U: int = 5
    cluster_root: float = 1.0
    cluster_tip: float = 1.0

    def __post_init__(self) -> None:
        if self.num_U < 1:
            raise ValueError("num_U must be >= 1.")
        if self.cluster_root <= 0.0:
            raise ValueError("cluster_root must be > 0.")
        if self.cluster_tip <= 0.0:
            raise ValueError("cluster_tip must be > 0.")

    def __str__(self) -> str:
        return (
            "WingSegment:\n"
            f"  id: {self.id}\n"
            f"  span: {self.span:.3f} m\n"
            f"  root_chord: {self.root_chord:.3f} m\n"
            f"  tip_chord: {self.tip_chord:.3f} m\n"
            f"  sweep_deg: {self.sweep_deg:.3f} deg\n"
            f"  dihedral_deg: {self.dihedral_deg:.3f} deg\n"
            f"  twist_deg: {self.twist_deg:.3f} deg\n"
            f"  sweep_ref_loc: {self.sweep_ref_loc:.3f} (-)\n"
            f"  twist_ref_loc: {self.twist_ref_loc:.3f} (-)\n"
            f"  num_U: {self.num_U:d} (-)\n"
            f"  cluster_root: {self.cluster_root:.3f} (-)\n"
            f"  cluster_tip: {self.cluster_tip:.3f} (-)"
        )


# ----------------------------------------------------------------------
# Example usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example: instantiate one wing segment and print its summary.
    wing_segment = WingSegment(
        id="WS_DEMO_01",
        span=4.0,
        root_chord=2.0,
        tip_chord=1.4,
        sweep_deg=12.0,
        dihedral_deg=4.0,
        twist_deg=-1.0,
        sweep_ref_loc=0.25,
        twist_ref_loc=0.25,
        )

    print(wing_segment)