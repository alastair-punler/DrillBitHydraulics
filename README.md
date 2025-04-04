# Drill Bit Hydraulics Calculator
https://drillbithydraulics.onrender.com/
A web-based calculator for determining pressure loss through drill bit nozzles and calculating Hydraulic Horsepower per Square Inch (HSI) in drilling operations.

## Overview

This application provides real-time calculations for:
- Pressure loss through drill bit nozzles
- Hydraulic Horsepower per Square Inch (HSI)
- Support for multiple nozzle configurations
- Flow rate optimization


## Technical Details

The calculator uses industry-standard formulas for drilling hydraulics calculations as presented in:

> Lapeyrouse, Norton J. (2002). "Formulas and Calculations for Drilling, Production, and Workover." Gulf Professional Publishing, 2nd Edition. ISBN: 0-7506-7530-X

### Core Equations

The pressure drop through bit nozzles is calculated using:

```
Pressure Loss = (MW × Q²) / (12031 × TFA²)
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
- Bit Area = Area of the drill bit (in²)

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
   - Nozzle sizes (in 32nds of an inch)
   - Mud weight/density
   - Flow rate
   - Bit size

2. The calculator will automatically compute:
   - Total Flow Area (TFA)
   - Pressure loss through nozzles
   - HSI value

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Primary reference: "Formulas and Calculations for Drilling, Production, and Workover" by Norton J. Lapeyrouse
- Icons and graphics: Various open-source contributors



