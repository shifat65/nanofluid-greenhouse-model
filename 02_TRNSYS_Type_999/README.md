# TRNSYS Type 999: Nanofluid Greenhouse

To use this component, compile `NanofluidGreenhouse.f90` using your TRNSYS Fortran compiler and load `NanofluidGH.trd` into TRNSYS Studio.

### Important TRNSYS Unit Conversions
TRNSYS uses `kJ/hr` while standard physics uses `Watts`. When entering parameters in TRNSYS Studio, use these values:

**For Case A (5mm):**
*   `C_air` (PAR 3): **0.289** (kJ/K)
*   `C_roof` (PAR 4): **5.0** (kJ/K)
*   `fraction_trans` (PAR 5): **0.4765**
*   `fraction_abs` (PAR 6): **0.5235**
*   `m_dot` (PAR 7): **360.0** (kg/hr)
*   `cp_fluid` (PAR 8): **4.0** (kJ/kg-K)

**For Case B (10mm):**
*   `C_roof` (PAR 4): **10.0** 
*   `fraction_trans` (PAR 5): **0.4386**
*   `fraction_abs` (PAR 6): **0.5614**
*   `m_dot` (PAR 7): **720.0**

**For Case C (15mm):**
*   `C_roof` (PAR 4): **15.0** 
*   `fraction_trans` (PAR 5): **0.4007**
*   `fraction_abs` (PAR 6): **0.5993**
*   `m_dot` (PAR 7): **1080.0**