"""Tests for the FiniteWing class."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def finitewing_types(monkeypatch):
    """Load FiniteWing with a stubbed OpenVSP bootstrap module."""
    aerodemo_src = Path(__file__).resolve().parents[1] / "src" / "aerodemo"
    monkeypatch.syspath_prepend(str(aerodemo_src))

    fake_vsp = types.SimpleNamespace(
        NO_END_CAP=0,
        FLAT_END_CAP=1,
        ROUND_END_CAP=2,
    )

    fake_bootstrap = types.ModuleType("_vsppytools_bootstrap")
    setattr(fake_bootstrap, "import_openvsp_from_local_vsppytools", lambda: fake_vsp)
    monkeypatch.setitem(sys.modules, "_vsppytools_bootstrap", fake_bootstrap)

    # Force fresh imports so the bootstrap stub is used.
    for name in ("AirfoilSpec", "WingSegment", "FiniteWing"):
        sys.modules.pop(name, None)

    airfoil_spec_mod = importlib.import_module("AirfoilSpec")
    wing_segment_mod = importlib.import_module("WingSegment")
    finite_wing_mod = importlib.import_module("FiniteWing")

    return (
        finite_wing_mod.FiniteWing,
        wing_segment_mod.WingSegment,
        airfoil_spec_mod.AirfoilSpec,
        fake_vsp,
    )


def test_default_init_creates_consistent_segments_and_stations(finitewing_types):
    FiniteWing, _, _, _ = finitewing_types

    wing = FiniteWing()

    assert len(wing.segments) == 1
    assert len(wing.station_airfoils) == 2
    assert wing.station_airfoils[0] is not wing.station_airfoils[1]


def test_init_raises_for_station_airfoil_count_mismatch(finitewing_types):
    FiniteWing, _, AirfoilSpec, _ = finitewing_types

    with pytest.raises(ValueError, match="station_airfoils"):
        FiniteWing(station_airfoils=[AirfoilSpec()])


def test_init_raises_for_non_continuous_segment_chords(finitewing_types):
    FiniteWing, WingSegment, _, _ = finitewing_types

    segments = [
        WingSegment(root_chord=2.0, tip_chord=1.5),
        WingSegment(root_chord=1.4, tip_chord=1.0),
    ]

    with pytest.raises(ValueError, match="must match"):
        FiniteWing(segments=segments)


def test_cap_enum_mapping_and_validation(finitewing_types):
    FiniteWing, _, _, fake_vsp = finitewing_types
    wing = FiniteWing()

    assert wing._cap_enum("None") == fake_vsp.NO_END_CAP
    assert wing._cap_enum("flat") == fake_vsp.FLAT_END_CAP
    assert wing._cap_enum("ROUND") == fake_vsp.ROUND_END_CAP

    with pytest.raises(ValueError, match="Cap shape"):
        wing._cap_enum("square")


def test_save_requires_build_first(finitewing_types):
    FiniteWing, _, _, _ = finitewing_types
    wing = FiniteWing()

    with pytest.raises(RuntimeError, match="Call build\(\) before save\(\)"):
        wing.save("out.vsp3")
