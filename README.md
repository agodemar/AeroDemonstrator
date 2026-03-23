# AeroDemonstrator

A collection of aerodynamic demonstration projects showcasing the features of
airfoils, finite wings, wing–fuselage, and complete aircraft configurations
(wing–fuselage–horizontal tail–vertical tail) including movable control
surfaces (ailerons, flaps, elevator, rudder).

Most code examples use the [OpenVSP Python API](https://openvsp.org/pyapi_docs/latest/)
— in particular the VSPAero calculation module — and are presented as
[Jupyter notebooks](https://jupyter.org/) with supporting Python classes.

## Project Structure

```
AeroDemonstrator/
├── notebooks/                  # Jupyter notebook demonstrations
│   ├── 01_airfoil/             # Beginner: NACA airfoil geometry & aerodynamics
│   ├── 02_finite_wing/         # Intermediate: VLM, induced drag, span loading
│   ├── 03_wing_fuselage/       # Intermediate: OpenVSP wing–fuselage model
│   └── 04_complete_aircraft/   # Advanced: full config + control surfaces
├── src/
│   └── aerodemo/               # Python utility package
│       ├── naca_airfoil.py     # NACA 4- and 5-digit airfoil generators
│       ├── vlm.py              # Vortex Lattice Method solver
│       └── openvsp_utils.py    # OpenVSP API helpers
├── tests/                      # pytest unit tests
├── docs/                       # Sphinx documentation
│   ├── conf.py
│   ├── index.rst
│   ├── installation.rst
│   ├── notebooks.rst
│   └── api/                    # Auto-generated API reference
└── pyproject.toml
```

## Notebook Overview

| # | Notebook | Level | Topics |
|---|----------|-------|--------|
| 01 | `airfoil_geometry_aerodynamics.ipynb` | Beginner | NACA 4/5-digit geometry, camber/thickness, thin-airfoil CL |
| 02 | `finite_wing_vlm.ipynb` | Intermediate | VLM, induced drag, spanwise loading, aspect ratio effects |
| 03 | `wing_fuselage_openvsp.ipynb` | Intermediate | OpenVSP model, VSPAero VLM, fuselage–wing interaction |
| 04 | `full_aircraft_openvsp.ipynb` | Advanced | Full aircraft, stability, elevator/aileron/rudder/flap effectiveness |

## Installation

```bash
# Clone the repository
git clone https://github.com/agodemar/AeroDemonstrator.git
cd AeroDemonstrator

# Install the package and dependencies
pip install -e .

# (Optional) Install documentation build dependencies
pip install -e ".[docs]"

# (Optional) Install OpenVSP for 3D geometry and VSPAero analysis
pip install openvsp
```

## Running the Notebooks

```bash
jupyter notebook notebooks/
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Building the Documentation

```bash
cd docs
make html
# Open docs/_build/html/index.html
```

## Dependencies

- Python ≥ 3.9
- NumPy, SciPy, Matplotlib
- Jupyter / JupyterLab
- [OpenVSP](https://openvsp.org) (optional, for 3D notebooks)
- [Sphinx](https://www.sphinx-doc.org) with RTD theme (for documentation)

## License

GNU Lesser General Public License v2.1 — see [LICENSE](LICENSE).
