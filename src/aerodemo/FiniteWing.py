from typing import Optional, List
import copy
from _vsppytools_bootstrap import import_openvsp_from_local_vsppytools
from AirfoilSpec import AirfoilSpec
from WingSegment import WingSegment

vsp = import_openvsp_from_local_vsppytools()

class FiniteWing:
    """
    Object-oriented OpenVSP finite wing builder.

    Constructor defaults:
        name = "FiniteWing"
            Geometry name used inside OpenVSP.

        mirrored = True
            Creates a mirrored wing by setting planar symmetry about XZ.
            This is the default for a conventional left-right wing.

        segments = None
            If omitted, one default segment is created:
                WingSegment()

        station_airfoils = None
            If omitted, all stations use the same default airfoil:
                AirfoilSpec()
            The expected number of stations is:
                len(segments) + 1

        root_incidence_deg = 0.0
            Root incidence angle in degrees.

        rotate_airfoils_with_dihedral = True
            Requests OpenVSP to rotate the airfoil orientation consistently
            with the wing dihedral.

        root_cap_shape = "Flat"
            Root cap shape. Allowed: "None", "Flat", "Round".
            On a mirrored wing, the root cap is usually not visually critical,
            but it is still exposed here.

        tip_cap_shape = "Flat"
            Tip cap shape. Allowed: "None", "Flat", "Round".

        root_cap_length = 0.0
            Root cap length parameter. Mostly relevant for rounded caps.

        tip_cap_length = 0.20
            Tip cap length parameter. Gives a visible rounded tip when
            tip_cap_shape == "Round".

        root_cap_strength = 1.0
            Root cap strength parameter.

        tip_cap_strength = 1.0
            Tip cap strength parameter.

        x_location = 0.0, y_location = 0.0, z_location = 0.0
            Geometry placement.

        x_rotation = 0.0, y_rotation = 0.0, z_rotation = 0.0
            Geometry orientation in degrees.

        clear_model_first = True
            Clears the current OpenVSP model before creating the wing.
    """

    _CAP_MAP = {
        "none": vsp.NO_END_CAP,
        "flat": vsp.FLAT_END_CAP,
        "round": vsp.ROUND_END_CAP,
    }

    def __init__(
        self,
        name: str = "FiniteWing",
        mirrored: bool = True,
        segments: Optional[List[WingSegment]] = None,
        station_airfoils: Optional[List[AirfoilSpec]] = None,
        root_incidence_deg: float = 0.0,
        rotate_airfoils_with_dihedral: bool = True,
        root_cap_shape: str = "Flat",
        tip_cap_shape: str = "Flat",
        root_cap_length: float = 0.0,
        tip_cap_length: float = 0.20,
        root_cap_strength: float = 1.0,
        tip_cap_strength: float = 1.0,
        x_location: float = 0.0,
        y_location: float = 0.0,
        z_location: float = 0.0,
        x_rotation: float = 0.0,
        y_rotation: float = 0.0,
        z_rotation: float = 0.0,
        clear_model_first: bool = True,
    ) -> None:
        self.name = name
        self.mirrored = mirrored
        self.root_incidence_deg = root_incidence_deg
        self.rotate_airfoils_with_dihedral = rotate_airfoils_with_dihedral

        self.root_cap_shape = root_cap_shape
        self.tip_cap_shape = tip_cap_shape
        self.root_cap_length = root_cap_length
        self.tip_cap_length = tip_cap_length
        self.root_cap_strength = root_cap_strength
        self.tip_cap_strength = tip_cap_strength

        self.x_location = x_location
        self.y_location = y_location
        self.z_location = z_location
        self.x_rotation = x_rotation
        self.y_rotation = y_rotation
        self.z_rotation = z_rotation

        self.clear_model_first = clear_model_first

        self.segments: List[WingSegment] = segments if segments is not None else [WingSegment()]
        self._validate_segments()

        if station_airfoils is None:
            default_af = AirfoilSpec()
            self.station_airfoils = [
                copy.deepcopy(default_af) for _ in range(len(self.segments) + 1)
            ]
        else:
            if len(station_airfoils) != len(self.segments) + 1:
                raise ValueError(
                    "station_airfoils must contain len(segments) + 1 entries "
                    "(one airfoil per spanwise station)."
                )
            self.station_airfoils = station_airfoils

        self.wing_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self) -> str:
        """Create the wing in OpenVSP and return the geometry ID."""
        if self.clear_model_first:
            vsp.ClearVSPModel()

        self.wing_id = vsp.AddGeom("WING", "")
        vsp.SetGeomName(self.wing_id, self.name)

        self._apply_global_transform()
        self._apply_symmetry()
        self._ensure_section_count(len(self.segments))

        # == End caps ==
        # self._apply_root_and_tip_caps() # Not working 
        self._apply_tip_cap() # Only apply tip cap for now

        self._apply_root_incidence()
        self._apply_segments()
        self._apply_station_airfoils()

        vsp.Update()
        return self.wing_id

    def save(self, filename: str = "finite_wing.vsp3") -> None:
        """Save the current model to a .vsp3 file."""
        if self.wing_id is None:
            raise RuntimeError("Call build() before save().")

        vsp.SetVSP3FileName(filename)
        vsp.WriteVSPFile(vsp.GetVSPFileName(), vsp.SET_ALL)

    def __str__(self) -> str:
        if self.segments:
            segments_text = "\n".join(
                "    " + str(seg).replace("\n", "\n    ") for seg in self.segments
            )
        else:
            segments_text = "    (none)"

        if self.station_airfoils:
            airfoils_text = "\n".join(
                "    " + str(af).replace("\n", "\n    ") for af in self.station_airfoils
            )
        else:
            airfoils_text = "    (none)"

        return (
            "FiniteWing:\n"
            f"  name: {self.name}\n"
            f"  wing_id: {self.wing_id}\n"
            f"  mirrored: {self.mirrored}\n"
            f"  root_incidence_deg: {self.root_incidence_deg:.3f} deg\n"
            f"  rotate_airfoils_with_dihedral: {self.rotate_airfoils_with_dihedral}\n"
            f"  root_cap_shape: {self.root_cap_shape}\n"
            f"  tip_cap_shape: {self.tip_cap_shape}\n"
            f"  root_cap_length: {self.root_cap_length:.3f} m\n"
            f"  tip_cap_length: {self.tip_cap_length:.3f} m\n"
            f"  root_cap_strength: {self.root_cap_strength:.3f} (-)\n"
            f"  tip_cap_strength: {self.tip_cap_strength:.3f} (-)\n"
            f"  location_xyz: ({self.x_location:.3f}, {self.y_location:.3f}, {self.z_location:.3f}) m\n"
            f"  rotation_xyz: ({self.x_rotation:.3f}, {self.y_rotation:.3f}, {self.z_rotation:.3f}) deg\n"
            f"  clear_model_first: {self.clear_model_first}\n"
            f"  num_segments: {len(self.segments)}\n"
            f"  segments:\n{segments_text}\n"
            f"  num_station_airfoils: {len(self.station_airfoils)}\n"
            f"  station_airfoils:\n{airfoils_text}"
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_segments(self) -> None:
        """Enforce chord continuity from one panel to the next."""
        if not self.segments:
            raise ValueError("At least one segment is required.")

        for i in range(1, len(self.segments)):
            prev_tip = self.segments[i - 1].tip_chord
            this_root = self.segments[i].root_chord
            if abs(prev_tip - this_root) > 1e-10:
                raise ValueError(
                    f"Segment {i} root_chord ({this_root}) must match "
                    f"segment {i - 1} tip_chord ({prev_tip}) for a continuous wing."
                )

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _wing_group(self) -> str:
        return "WingGeom"

    def _section_group(self, section_index: int) -> str:
        return f"XSec_{section_index}"

    def _curve_group(self, station_index: int) -> str:
        return f"XSecCurve_{station_index}"

    def _require_wing_id(self) -> str:
        if self.wing_id is None:
            raise RuntimeError("Wing has not been created yet.")
        return self.wing_id

    def _xsec_surf_id(self) -> str:
        return vsp.GetXSecSurf(self._require_wing_id(), 0)

    def _xsec_id(self, station_index: int) -> str:
        return vsp.GetXSec(self._xsec_surf_id(), station_index)

    def _set_parm(
        self,
        container_id: str,
        parm_name: str,
        group_name: str,
        value: float,
        required: bool = True,
    ) -> None:
        pid = vsp.FindParm(container_id, parm_name, group_name)
        if not vsp.ValidParm(pid):
            if required:
                raise RuntimeError(
                    f"Parameter not found: group='{group_name}', parm='{parm_name}'"
                )
            return
        vsp.SetParmValUpdate(pid, float(value))

    def _set_optional_parm(self, container_id: str, parm_name: str, group_name: str, value: float) -> None:
        self._set_parm(container_id, parm_name, group_name, value, required=False)

    def _bool_value(self, flag: bool) -> float:
        return 1.0 if flag else 0.0

    def _cap_enum(self, cap_name: str) -> int:
        key = cap_name.strip().lower()
        if key not in self._CAP_MAP:
            raise ValueError("Cap shape must be one of: 'None', 'Flat', 'Round'.")
        return self._CAP_MAP[key]

    # ------------------------------------------------------------------
    # Geometry setup
    # ------------------------------------------------------------------

    def _apply_global_transform(self) -> None:
        wing_id = self._require_wing_id()
        self._set_parm(wing_id, "X_Rel_Location", "XForm", self.x_location)
        self._set_parm(wing_id, "Y_Rel_Location", "XForm", self.y_location)
        self._set_parm(wing_id, "Z_Rel_Location", "XForm", self.z_location)

        self._set_parm(wing_id, "X_Rel_Rotation", "XForm", self.x_rotation)
        self._set_parm(wing_id, "Y_Rel_Rotation", "XForm", self.y_rotation)
        self._set_parm(wing_id, "Z_Rel_Rotation", "XForm", self.z_rotation)

        vsp.Update()

    def _apply_symmetry(self) -> None:
        wing_id = self._require_wing_id()
        sym_val = vsp.SYM_XZ if self.mirrored else 0
        self._set_parm(wing_id, "Sym_Planar_Flag", "Sym", sym_val)
        vsp.Update()

    def _ensure_section_count(self, n_segments: int) -> None:
        """
        Make sure the wing has exactly n_segments panels.
        A wing with N panels has N+1 spanwise stations.
        """
        wing_id = self._require_wing_id()

        xsec_surf = self._xsec_surf_id()
        target_xsecs = n_segments + 1

        # Insert new sections before the terminal tip station until the count matches.
        while vsp.GetNumXSec(xsec_surf) < target_xsecs:
            insert_index = vsp.GetNumXSec(xsec_surf) - 1
            vsp.InsertXSec(wing_id, insert_index, vsp.XS_FOUR_SERIES)
            vsp.Update()
            xsec_surf = self._xsec_surf_id()

        # Remove extra interior sections if needed.
        while vsp.GetNumXSec(xsec_surf) > target_xsecs:
            cut_index = vsp.GetNumXSec(xsec_surf) - 2
            vsp.CutXSec(wing_id, cut_index)
            vsp.Update()
            xsec_surf = self._xsec_surf_id()

    def _apply_tip_cap(self) -> None:
        wing_id = self._require_wing_id()

        self._set_optional_parm(
            wing_id, "CapUMaxOption", "EndCap", self._cap_enum(self.tip_cap_shape)
        )

        vsp.Update()

    def _apply_root_cap(self) -> None:
        wing_id = self._require_wing_id()

        self._set_optional_parm(
            wing_id, "CapUMinOption", "EndCap", self._cap_enum(self.root_cap_shape)
        )

        vsp.Update()

    def _apply_root_incidence(self) -> None:
        wing_id = self._require_wing_id()
        self._set_optional_parm(
            wing_id, "Twist", self._section_group(0), self.root_incidence_deg
        )
        self._set_optional_parm(
            wing_id, "Twist_Location", self._section_group(0), 0.25
        )

        # Global flag used by the stock OpenVSP wing example.
        self._set_optional_parm(
            wing_id,
            "RotateAirfoilMatchDideralFlag",
            self._wing_group(),
            self._bool_value(self.rotate_airfoils_with_dihedral),
        )
        vsp.Update()

    def _apply_segments(self) -> None:
        wing_id = self._require_wing_id()

        for i, seg in enumerate(self.segments, start=1):
            # Use section drivers: span, root chord, tip chord.
            vsp.SetDriverGroup(
                wing_id,
                i,
                vsp.SPAN_WSECT_DRIVER,
                vsp.ROOTC_WSECT_DRIVER,
                vsp.TIPC_WSECT_DRIVER,
            )
            vsp.Update()

            g = self._section_group(i)
            self._set_parm(wing_id, "Span", g, seg.span)
            self._set_parm(wing_id, "Root_Chord", g, seg.root_chord)
            self._set_parm(wing_id, "Tip_Chord", g, seg.tip_chord)
            self._set_parm(wing_id, "Sweep", g, seg.sweep_deg)
            self._set_parm(wing_id, "Sweep_Location", g, seg.sweep_ref_loc)
            self._set_parm(wing_id, "Dihedral", g, seg.dihedral_deg)
            self._set_parm(wing_id, "Twist", g, seg.twist_deg)
            self._set_parm(wing_id, "Twist_Location", g, seg.twist_ref_loc)

            # Per-section discretization controls.
            self._set_optional_parm(wing_id, "SectTess_U", g, seg.num_U)
            self._set_optional_parm(wing_id, "InCluster", g, seg.cluster_root)
            self._set_optional_parm(wing_id, "OutCluster", g, seg.cluster_tip)

            # Per-section flag, when present.
            self._set_optional_parm(
                wing_id,
                "RotateMatchDideralFlag",
                g,
                self._bool_value(self.rotate_airfoils_with_dihedral),
            )

            # OpenVSP wing sections are connected, so updating after each panel
            # is safer than changing everything in one batch.
            vsp.Update()

    # ------------------------------------------------------------------
    # Airfoils
    # ------------------------------------------------------------------

    def _apply_station_airfoils(self) -> None:
        for station_index, spec in enumerate(self.station_airfoils):
            self._apply_one_airfoil(station_index, spec)

    def _apply_one_airfoil(self, station_index: int, spec: AirfoilSpec) -> None:
        wing_id = self._require_wing_id()
        xsec_surf = self._xsec_surf_id()
        xsec_id = self._xsec_id(station_index)
        curve_group = self._curve_group(station_index)

        kind = spec.kind.strip().lower()

        if kind == "naca4":
            vsp.ChangeXSecShape(xsec_surf, station_index, vsp.XS_FOUR_SERIES)
            vsp.Update()

            self._set_parm(wing_id, "Camber", curve_group, spec.camber)
            self._set_parm(wing_id, "CamberLoc", curve_group, spec.camber_loc)
            self._set_parm(wing_id, "ThickChord", curve_group, spec.thickness)
            self._set_optional_parm(
                wing_id,
                "SharpTEFlag",
                curve_group,
                self._bool_value(spec.sharp_te),
            )
            vsp.Update()
            return

        if kind == "file":
            if not spec.file_path:
                raise ValueError("file airfoil requires file_path to be set.")

            vsp.ChangeXSecShape(xsec_surf, station_index, vsp.XS_FILE_AIRFOIL)
            vsp.Update()

            vsp.ReadFileAirfoil(xsec_id, spec.file_path)
            vsp.Update()
            return

        if kind == "custom":
            if spec.xsec_type is None:
                raise ValueError("custom airfoil requires xsec_type to be set.")

            vsp.ChangeXSecShape(xsec_surf, station_index, spec.xsec_type)
            vsp.Update()

            # Apply any custom XSecCurve parameters supplied by the user.
            for parm_name, value in spec.extra_parms.items():
                self._set_parm(wing_id, parm_name, curve_group, value)
            vsp.Update()
            return

        raise ValueError(
            "Unsupported airfoil kind. Use 'naca4', 'file', or 'custom'."
        )


# ----------------------------------------------------------------------
# Example usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example: configure a 2-panel finite wing and print its summary.
    segments = [
        WingSegment(
            id="WS_ROOT",
            span=3.0,
            root_chord=2.0,
            tip_chord=1.5,
            sweep_deg=10.0,
            dihedral_deg=3.0,
            twist_deg=-1.0,
        ),
        WingSegment(
            id="WS_TIP",
            span=2.0,
            root_chord=1.5,
            tip_chord=1.0,
            sweep_deg=15.0,
            dihedral_deg=5.0,
            twist_deg=-2.0,
        ),
    ]

    station_airfoils = [
        AirfoilSpec(kind="naca4", camber=0.02, camber_loc=0.4, thickness=0.12),
        AirfoilSpec(kind="naca4", camber=0.01, camber_loc=0.4, thickness=0.11),
        AirfoilSpec(kind="naca4", camber=0.0, camber_loc=0.4, thickness=0.10),
    ]

    wing = FiniteWing(
        name="FW_DEMO_01",
        mirrored=True,
        segments=segments,
        station_airfoils=station_airfoils,
        root_incidence_deg=1.0,
        tip_cap_shape="Round",
        tip_cap_length=0.2,
    )

    print(wing)

    wing.build()
    wing.save("test_FiniteWing.vsp3")
    print("Saved: test_FiniteWing.vsp3")
