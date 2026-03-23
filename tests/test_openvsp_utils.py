"""Tests for OpenVSP utility functions."""

import pytest
from aerodemo.openvsp_utils import check_openvsp


def test_check_openvsp_returns_bool():
    result = check_openvsp()
    assert isinstance(result, bool)


def test_init_vsp_raises_without_openvsp():
    from aerodemo.openvsp_utils import check_openvsp, init_vsp
    if not check_openvsp():
        with pytest.raises(ImportError):
            init_vsp()
    else:
        init_vsp()  # Should not raise


def test_add_wing_returns_none_without_openvsp():
    from aerodemo.openvsp_utils import check_openvsp, add_wing
    if not check_openvsp():
        result = add_wing()
        assert result is None


def test_run_vspaero_returns_none_without_openvsp():
    from aerodemo.openvsp_utils import check_openvsp, run_vspaero
    if not check_openvsp():
        result = run_vspaero()
        assert result is None
