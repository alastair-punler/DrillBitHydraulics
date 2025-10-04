# Drill Bit Hydraulics Calculator
https://drillbithydraulics-production.up.railway.app/
A web-based calculator for determining pressure loss through drill bit nozzles and calculating Hydraulic Horsepower per Square Inch (HSI) in drilling operations.

## Overview

This application provides real-time calculations for:
- Pressure loss through drill bit nozzles
- Hydraulic Horsepower per Square Inch (HSI)
- Jet Impact Force (JIF)
- Support for multiple nozzle configurations
- Flow rate optimization


## Technical Details

The calculator uses industry-standard formulas for drilling hydraulics calculations as presented in:

> Lapeyrouse, Norton J. (2002). "Formulas and Calculations for Drilling, Production, and Workover." Gulf Professional Publishing, 2nd Edition. ISBN: 0-7506-7530-X

### Core Equations

The pressure drop through bit nozzles is calculated using:

```
Pressure Loss = (MW × Q²) / (10858 × TFA²)
```

Where:
- Pressure Loss = Pressure loss through bit (psi)
- MW = Mud Weight (ppg)
- Q = Flow Rate (gpm)
- TFA = Total Flow Area (in²)

Hydraulic Horsepower per Square Inch (HSI) is calculated using:

```
HSI = (Pressure Loss × Q) / (1714 × Bit Area)
```

Where:
- HSI = Hydraulic Horsepower per Square Inch
- Pressure Loss = Pressure loss through bit (psi)
- Q = Flow Rate (gpm)
- Bit Area = Area of the drill bit (in²) (Note: In the app, Bit Size (diameter) is used, and area is calculated (πd²/4), though this formula typically uses bit area directly)

### Jet Impact Force (JIF)

Jet Impact Force is a measure of the hydraulic energy from the drilling fluid jets exiting the bit nozzles. This force helps clean the bottom of the wellbore and can influence the rate of penetration (ROP). It is calculated in pounds (lbs).

The formulas used in this application are:

1.  **Nozzle Velocity (Vn):**
    ```
    Vn (ft/s) = 0.32086 × Q (gpm) / TFA (in²)
    ```
    Where:
    - Vn = Nozzle Velocity in feet per second
    - Q = Flow Rate in gallons per minute
    - TFA = Total Flow Area in square inches (calculated from nozzle sizes or direct input)

2.  **Jet Impact Force (JIF):**
    ```
    JIF (lbs) = 0.000526 × MW (ppg) × Q (gpm) × Vn (ft/s)
    ```
    Where:
    - JIF = Jet Impact Force in pounds
    - MW = Mud Weight in pounds per gallon (converted from SG if necessary)
    - Q = Flow Rate in gallons per minute
    - Vn = Nozzle Velocity in feet per second (as calculated in the previous step)

This feature has been implemented in the calculator, providing users with another key hydraulic parameter for analysis and optimization of drilling operations.

## Installation

1. Clone the repository:
```powershell
git clone https://github.com/alastair-punler/DrillBitHydraulics.git
cd DrillBitHydraulics
```

2. Create a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Run the application:
```powershell
python app.py
```

The application will be available at `http://localhost:5000` in your web browser.

## Usage

1. Enter the required inputs:
   - Nozzle sizes (in 32nds of an inch) or Direct TFA
   - Mud weight/density (ppg or SG)
   - Flow rate (GPM) - single value or a range (e.g., 800 or 800-1200)
   - Bit size (inches)

2. The calculator will automatically compute:
   - Total Flow Area (TFA)
   - Pressure loss through nozzles (PSI)
   - HSI value
   - Jet Impact Force (lbs)

For range inputs, charts will be displayed for Pressure Loss, HSI, and Jet Impact Force versus Flow Rate.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Primary reference: "Formulas and Calculations for Drilling, Production, and Workover" by Norton J. Lapeyrouse
- Icons and graphics: Various open-source contributors
