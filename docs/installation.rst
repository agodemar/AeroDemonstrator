Installation
============

Requirements
------------

- Python 3.9 or later
- NumPy ≥ 1.24
- SciPy ≥ 1.10
- Matplotlib ≥ 3.7
- Jupyter / JupyterLab

Optional (for OpenVSP notebooks):

- ``openvsp`` Python API — see https://openvsp.org

Quick Start (conda)
-------------------

The recommended way to set up the environment is with `conda
<https://docs.conda.io>`_, using the provided ``environment.yml`` file.

1. **Clone the repository**::

      git clone https://github.com/agodemar/AeroDemonstrator.git
      cd AeroDemonstrator

2. **Create and activate the conda environment**::

      conda env create -f environment.yml
      conda activate aerodemo

3. **Install the package in editable mode**::

      pip install -e .

4. **Launch Jupyter**::

      jupyter notebook notebooks/

Quick Start (pip)
-----------------

1. **Clone the repository**::

      git clone https://github.com/agodemar/AeroDemonstrator.git
      cd AeroDemonstrator

2. **Install the package and dependencies**::

      pip install -e ".[docs,dev]"

   Or just the runtime requirements::

      pip install -r requirements.txt

3. **Install the package in editable mode**::

      pip install -e .

4. **Launch Jupyter**::

      jupyter notebook notebooks/

OpenVSP Installation
--------------------

The notebooks in ``03_wing_fuselage`` and ``04_complete_aircraft`` use the
OpenVSP Python API for 3D geometry modeling and VSPAero analysis.

To install OpenVSP::

   pip install openvsp

Or download prebuilt wheels from https://openvsp.org.

.. note::

   If OpenVSP is not installed, the notebooks automatically fall back to the
   built-in VLM solver for aerodynamic analysis.

Building the Documentation
--------------------------

The documentation is built with Sphinx::

   cd docs
   pip install -e "../[docs]"
   make html

The built HTML will be at ``docs/_build/html/index.html``.
