# Nanofluid Spectral Splitting Greenhouse Model

This repository contains a validated thermal model for a Nanofluid Spectral Splitting Greenhouse roof. The model simulates the absorption of Near-Infrared (NIR) radiation by a nanofluid to cool the greenhouse environment while simultaneously harvesting solar thermal energy.

## Repository Structure
*   `01_Python_Prototype/`: Contains the Python-based object-oriented model used for rapid prototyping and validation against experimental data.
*   `02_TRNSYS_Type_999/`: Contains the Fortran source code (`.f90`) and TRNSYS Proforma (`.trd`) to run the model in TRNSYS Simulation Studio.

## Getting Started

### Python Prototype
1. Navigate to `01_Python_Prototype/`.
2. Install dependencies: `pip install pandas numpy scipy matplotlib`.
3. Run `python prototype_sim.py` to generate the parametric comparison plots (5mm, 10mm, 15mm).

### TRNSYS Implementation
1. Navigate to `02_TRNSYS_Type_999/`.
2. Follow the instructions in the specific `README.md` to compile the Fortran code and import the `.trd` file into TRNSYS Studio.

## Model Physics
The model calculates the spectral split using numerical integration (Trapezoidal rule) over the 350–1600 nm wavelength range based on the AM1.5G solar spectrum. 
*   **Visible Light (VIS):** Transmitted to plants.
*   **Near-Infrared (NIR):** Absorbed by the nanofluid and removed via fluid circulation.