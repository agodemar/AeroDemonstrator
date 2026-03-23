AeroDemonstrator Documentation
===============================

.. image:: https://img.shields.io/badge/python-3.9%2B-blue
   :alt: Python 3.9+

.. image:: https://img.shields.io/badge/license-LGPLv2.1-green
   :alt: License: LGPLv2.1

**AeroDemonstrator** is a collection of aerodynamic demonstration projects
showcasing the aerodynamic features of airfoils, finite wings, and complete
aircraft configurations.

The project provides:

- **Jupyter notebooks** covering airfoil aerodynamics, finite wing theory,
  wing–fuselage configurations, and full aircraft with control surfaces
- **Python utility classes** for NACA airfoil generation, Vortex Lattice Method,
  and OpenVSP integration
- **OpenVSP integration** for 3D parametric geometry and VSPAero analysis

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation

.. toctree::
   :maxdepth: 2
   :caption: Notebooks

   notebooks

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/index

Project Overview
----------------

The code examples are organized by complexity level:

.. list-table::
   :header-rows: 1
   :widths: 10 25 65

   * - Level
     - Notebook
     - Topics
   * - Beginner
     - ``01_airfoil``
     - NACA airfoil geometry, thin-airfoil theory, CL vs. alpha
   * - Intermediate
     - ``02_finite_wing``
     - Vortex lattice method, induced drag, span loading, aspect ratio effects
   * - Intermediate
     - ``03_wing_fuselage``
     - OpenVSP geometry, wing–fuselage aerodynamics, VSPAero VLM
   * - Advanced
     - ``04_complete_aircraft``
     - Full aircraft with tails, control surfaces, stability & control

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
