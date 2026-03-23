Notebooks
=========

The demonstration notebooks are organized by complexity level and topic.
Each notebook is self-contained with explanations, equations, and visualizations.

.. note::

   To run the notebooks, first install the package::

      pip install -e .
      jupyter notebook notebooks/

Notebook 01 — Airfoil Geometry and Aerodynamics
-------------------------------------------------

**Level:** Beginner | **Location:** ``notebooks/01_airfoil/``

.. rubric:: airfoil_geometry_aerodynamics.ipynb

Introduces NACA airfoil geometry generation and fundamental aerodynamic
analysis using thin-airfoil theory.

**Topics covered:**

- NACA 4-digit airfoil coordinate generation (thickness + camber)
- NACA 5-digit airfoil family
- Airfoil visualization and shape analysis
- Thin-airfoil theory: lift curve slope, zero-lift angle
- Effect of camber on lift coefficient

**Key classes:** :class:`aerodemo.naca_airfoil.NACAFourDigit`,
:class:`aerodemo.naca_airfoil.NACAFiveDigit`

Notebook 02 — Finite Wing Aerodynamics (VLM)
---------------------------------------------

**Level:** Intermediate | **Location:** ``notebooks/02_finite_wing/``

.. rubric:: finite_wing_vlm.ipynb

Studies the aerodynamic behavior of finite wings using the Vortex Lattice
Method.

**Topics covered:**

- Wing geometry parameters: aspect ratio, taper ratio, sweep, dihedral
- Vortex Lattice Method (VLM) solver
- Spanwise lift distribution and comparison to elliptic ideal
- Induced drag and Oswald efficiency factor
- Effect of aspect ratio on aerodynamic performance

**Key classes:** :class:`aerodemo.vlm.WingGeometry`,
:class:`aerodemo.vlm.VortexLatticeMethod`

Notebook 03 — Wing–Fuselage Configuration with OpenVSP
-------------------------------------------------------

**Level:** Intermediate | **Location:** ``notebooks/03_wing_fuselage/``

.. rubric:: wing_fuselage_openvsp.ipynb

Demonstrates wing–fuselage geometry creation with the OpenVSP Python API
and aerodynamic analysis with VSPAero.

**Topics covered:**

- OpenVSP model creation (wing + fuselage)
- VSPAero VLM analysis configuration and execution
- CL, CDi, Cm coefficient extraction
- Comparison: OpenVSP vs. standalone VLM

**Key functions:** :func:`aerodemo.openvsp_utils.add_wing`,
:func:`aerodemo.openvsp_utils.add_fuselage`,
:func:`aerodemo.openvsp_utils.run_vspaero`

Notebook 04 — Full Aircraft with Control Surfaces
--------------------------------------------------

**Level:** Advanced | **Location:** ``notebooks/04_complete_aircraft/``

.. rubric:: full_aircraft_openvsp.ipynb

Builds a complete aircraft configuration (wing + fuselage + horizontal tail +
vertical tail) and analyzes stability and control surface effectiveness.

**Topics covered:**

- Full aircraft geometry with all lifting surfaces
- Horizontal and vertical tail sizing (volume coefficients)
- Longitudinal stability: CL-alpha, Cm-alpha, static margin
- Control surface effectiveness:

  - Aileron (roll) — dCl/dδ_a
  - Elevator (pitch) — dCm/dδ_e
  - Rudder (yaw) — dCn/dδ_r

- High-lift flap analysis

**Key functions:** :func:`aerodemo.openvsp_utils.add_horizontal_tail`,
:func:`aerodemo.openvsp_utils.add_vertical_tail`
