from __future__ import annotations

import sys
from pathlib import Path


def _find_vsppytools_root() -> Path | None:
    """Find local vsppytools root for both supported repository layouts."""
    this_dir = Path(__file__).resolve().parent
    candidates = [
        this_dir / "vsppytools",            # src/aerodemo/vsppytools
        this_dir.parent / "vsppytools",     # src/vsppytools
    ]

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def _configure_local_vsppytools_paths(vsppy_root: Path) -> None:
    """Add local vsppytools paths so `openvsp` can be imported in-place."""
    src_dir = vsppy_root.parent
    candidate_paths = [
        src_dir,
        vsppy_root,
        vsppy_root / "openvsp",
        vsppy_root / "openvsp_config",
    ]

    for path in candidate_paths:
        if path.is_dir():
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)


def _build_openvsp_import_diagnostic(err: ImportError) -> str:
    """Build an actionable message when OpenVSP native modules fail to load."""
    vsppy_root = _find_vsppytools_root()
    if vsppy_root is None:
        return (
            "OpenVSP import failed and no local vsppytools directory was found.\n"
            f"Original import error: {err}\n"
            "Expected one of these paths to exist:\n"
            f"- {Path(__file__).resolve().parent / 'vsppytools'}\n"
            f"- {Path(__file__).resolve().parent.parent / 'vsppytools'}"
        )

    openvsp_pkg_dir = vsppy_root / "openvsp" / "openvsp"
    openvsp_config_dir = vsppy_root / "openvsp_config"
    module_file = openvsp_pkg_dir / "_vsp.pyd"

    lines = [
        "OpenVSP local API was found, but its native extension could not be loaded.",
        f"Original import error: {err}",
        "",
        f"Active Python interpreter: {sys.version.split()[0]}",
        "",
        f"Resolved local vsppytools root: {vsppy_root}",
        "",
        "Checked locations:",
        f"- OpenVSP package dir: {openvsp_pkg_dir}",
        f"- _vsp extension present: {'yes' if module_file.is_file() else 'no'} ({module_file})",
        f"- openvsp_config dir: {openvsp_config_dir}",
        "",
        "Fix options:",
        "1) Ensure this repository contains a compatible OpenVSP Python build at the resolved local path.",
        f"2) If needed, add this folder to PATH before running Python: {openvsp_pkg_dir}",
        "3) Ensure Microsoft Visual C++ Redistributable (x64) is installed.",
    ]
    return "\n".join(lines)


def import_openvsp_from_local_vsppytools():
    """Import openvsp by bootstrapping local vsppytools paths."""
    try:
        vsppy_root = _find_vsppytools_root()
        if vsppy_root is None:
            raise ModuleNotFoundError(
                "Could not find local vsppytools directory. Expected one of: "
                "src/aerodemo/vsppytools or src/vsppytools."
            )

        _configure_local_vsppytools_paths(vsppy_root)
        import openvsp as vsp
        return vsp
    except ImportError as import_err:
        raise ImportError(_build_openvsp_import_diagnostic(import_err)) from import_err
