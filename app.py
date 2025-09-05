from flask import Flask, render_template, request, jsonify
import math
import numpy as np
from typing import List, Dict, Tuple
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')

# --- Constants ---
SG_TO_PPG_CONVERSION = 8.33
ANNULAR_VELOCITY_CONSTANT = 24.51 # Constant for AV in ft/min from GPM and inches

def convert_to_ppg(value, unit):
    """
    Convert density value to PPG
    
    Parameters:
    value (float): Density value
    unit (str): Unit of measurement ('ppg' or 'sg')
    
    Returns:
    float: Density in PPG
    """
    if unit.lower() == 'sg':
        return value * SG_TO_PPG_CONVERSION  # Convert SG to PPG
    return value  # Already in PPG

def calculate_total_flow_area(nozzles):
    """
    Calculate total flow area from nozzle sizes in 32nds of an inch
    
    Parameters:
    nozzles: list of tuples (size_in_32nds, quantity)
    
    Returns:
    float: Total flow area in square inches
    """
    total_area = 0
    for size_32, qty in nozzles:
        # Convert from 32nds to inches and calculate area
        diameter_inches = size_32 / 32
        area = (math.pi / 4) * (diameter_inches ** 2)
        total_area += area * qty
    return round(total_area, 4)

def calculate_bit_hydraulics(flow_rate, mud_density, density_unit, nozzles, bit_size, total_flow_area=None):
    """
    Calculate pressure loss and HSI through a drill bit
    
    Parameters:
    flow_rate (float): Flow rate in gallons per minute (GPM)
    mud_density (float): Mud density in PPG or SG
    density_unit (str): Unit of mud density ('ppg' or 'sg')
    nozzles: list of tuples (size_in_32nds, quantity) - only used if total_flow_area is None
    bit_size (float): Bit size in inches
    total_flow_area (float, optional): Direct TFA input in square inches
    
    Returns:
    dict: Pressure loss in PSI and HSI
    """
    # Convert density to PPG if needed
    mud_density_ppg = convert_to_ppg(mud_density, density_unit)
    
    # Use provided TFA or calculate from nozzles
    if total_flow_area is None:
        total_flow_area = calculate_total_flow_area(nozzles)
    
    # Calculate pressure loss using your formula
    pressure_loss = (mud_density_ppg * flow_rate**2) / (10858 * total_flow_area**2)
    
    # Calculate HSI using your formula
    hsi = (flow_rate * pressure_loss)*1.27 / (1714 * bit_size**2)
    
    # Calculate Jet Impact Force
    jet_impact_force = calculate_jet_impact_force(flow_rate, mud_density_ppg, total_flow_area)

    return {
        'pressure_loss': round(pressure_loss, 2),
        'hsi': round(hsi, 2),
        'total_flow_area': total_flow_area,
        'jet_impact_force': round(jet_impact_force, 2)
    }

def calculate_jet_impact_force(flow_rate, mud_density_ppg, total_flow_area):
    """
    Calculate Jet Impact Force (JIF) in pounds.

    Parameters:
    flow_rate (float): Flow rate in gallons per minute (GPM)
    mud_density_ppg (float): Mud density in pounds per gallon (PPG)
    total_flow_area (float): Total flow area in square inches (in²)

    Returns:
    float: Jet Impact Force in pounds (lbs)
    """
    if total_flow_area == 0:
        return 0 # Avoid division by zero

    # Calculate Nozzle Velocity (Vn) in ft/s
    # Vn = 0.32086 * GPM / TFA (in²)
    nozzle_velocity = 0.32086 * flow_rate / total_flow_area

    # Calculate Jet Impact Force (JIF) in lbs
    # JIF = 0.000526 * Mud Density (ppg) * Flow Rate (gpm) * Nozzle Velocity (ft/s)
    jet_impact_force = 0.000526 * mud_density_ppg * flow_rate * nozzle_velocity

    return jet_impact_force

def calculate_range_results(min_flow, max_flow, mud_density, density_unit, nozzles, bit_size, total_flow_area=None):
    """
    Calculate results for a range of flow rates in 50 GPM increments
    """
    flow_rates = list(range(int(min_flow), int(max_flow) + 50, 50))
    pressure_losses = []
    hsi_values = []
    jet_impact_force_values = []
    
    for flow_rate in flow_rates:
        result = calculate_bit_hydraulics(
            flow_rate, 
            mud_density, 
            density_unit, 
            nozzles, 
            bit_size,
            total_flow_area
        )
        pressure_losses.append(result['pressure_loss'])
        hsi_values.append(result['hsi'])
        jet_impact_force_values.append(result['jet_impact_force'])
    
    return {
        'flow_rates': flow_rates,
        'pressure_losses': pressure_losses,
        'hsi_values': hsi_values,
        'jet_impact_force_values': jet_impact_force_values,
        'avg_pressure_loss': round(sum(pressure_losses) / len(pressure_losses), 2),
        'avg_hsi': round(sum(hsi_values) / len(hsi_values), 2),
        'avg_jet_impact_force': round(sum(jet_impact_force_values) / len(jet_impact_force_values), 2)
    }

def calculate_annular_velocity(flow_rate: float, outer_diameter: float, inner_diameter: float) -> float:
    """
    Calculates annular velocity in ft/min.

    Formula: AV (ft/min) = (24.51 * Flow Rate (GPM)) / (ID^2 - OD^2)
    """
    if inner_diameter <= outer_diameter:
        raise ValueError("Inner Diameter (ID) must be greater than Outer Diameter (OD).")
    
    # Annular area in square inches
    annular_area = inner_diameter**2 - outer_diameter**2
    if annular_area == 0:
        raise ValueError("Inner and Outer diameters cannot be equal.")
        
    velocity = (ANNULAR_VELOCITY_CONSTANT * flow_rate) / annular_area
    return round(velocity, 2)

def calculate_av_range_results(min_flow, max_flow, geometries):
    """
    Calculates annular velocities for a range of flow rates.
    """
    flow_rates = list(range(int(min_flow), int(max_flow) + 50, 50))
    if not flow_rates: # Handle cases where min_flow is close to or greater than max_flow
        flow_rates = [int(min_flow)]

    results_by_section = []
    for i, geo in enumerate(geometries):
        od = float(geo['od'])
        id = float(geo['id'])
        section_name = geo.get('name', '').strip() or f"Section {i + 1}"
        
        section_velocities = []
        for flow_rate in flow_rates:
            velocity = calculate_annular_velocity(flow_rate, od, id)
            feedback = get_velocity_feedback(velocity)
            section_velocities.append({
                'velocity': velocity,
                **feedback
            })
        
        results_by_section.append({
            'section': section_name,
            'od': od,
            'id': id,
            'velocities': section_velocities
        })
        
    return {
        'flow_rates': flow_rates,
        'results_by_section': results_by_section
    }

def get_velocity_feedback(velocity: float) -> Dict[str, str]:
    """
    Provides a status and comment based on annular velocity for hole cleaning.
    
    Parameters:
    velocity (float): Annular velocity in ft/min.
    
    Returns:
    dict: A dictionary with 'status' and 'comment'.
    """
    if velocity >= 200:
        return {'status': 'optimal', 'comment': 'Optimal hole cleaning'}
    elif velocity >= 150:
        return {'status': 'minimum', 'comment': 'Minimum hole cleaning achieved'}
    else:
        return {'status': 'poor', 'comment': 'Poor hole cleaning'}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        flow_rate_data = data['flow_rate']
        mud_density = float(data['mud_density'])
        density_unit = data['density_unit']
        bit_size = float(data['bit_size'])
        input_method = data['input_method']
        
        # Calculate total flow area based on input method
        if input_method == 'nozzle':
            # Process nozzle data
            nozzles = []
            for nozzle in data['nozzles']:
                if nozzle['size'] and nozzle['quantity']:
                    nozzles.append((float(nozzle['size']), int(nozzle['quantity'])))
            
            if not nozzles:
                return jsonify({
                    'success': False,
                    'error': 'At least one nozzle size and quantity must be provided'
                }), 400
            
            # Calculate total flow area from nozzles
            total_flow_area = calculate_total_flow_area(nozzles)
        else:  # input_method == 'tfa'
            # Use direct TFA input
            total_flow_area = float(data['tfa'])
            if total_flow_area <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Total Flow Area must be greater than 0'
                }), 400
        
        if flow_rate_data['isRange']:
            # Calculate results for the range
            range_results = calculate_range_results(
                flow_rate_data['min'],
                flow_rate_data['max'],
                mud_density,
                density_unit,
                [(0, 1)],  # Dummy nozzle data since we're using TFA directly
                bit_size,
                total_flow_area  # Pass TFA directly
            )
            
            return jsonify({
                'success': True,
                'total_flow_area': total_flow_area,
                **range_results
            })
        else:
            # Calculate single value result
            results = calculate_bit_hydraulics(
                flow_rate_data['value'],
                mud_density,
                density_unit,
                [(0, 1)],  # Dummy nozzle data since we're using TFA directly
                bit_size,
                total_flow_area  # Pass TFA directly
            )
            
            return jsonify({
                'success': True,
                **results
            })
        
    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'error': f"Invalid input data: {e}"}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred in /calculate: {e}")
        return jsonify({
            'success': False,
            'error': "An internal server error occurred."
        }), 500

@app.route('/calculate_av', methods=['POST'])
def calculate_av():
    """Endpoint for Annular Velocity calculations."""
    try:
        data = request.get_json()
        flow_rate_data = data['flow_rate']
        geometries = data['geometries']

        if not geometries:
            return jsonify({'success': False, 'error': 'At least one geometry section is required.'}), 400

        if flow_rate_data.get('isRange'):
            # Handle range calculation
            range_results = calculate_av_range_results(
                flow_rate_data['min'],
                flow_rate_data['max'],
                geometries
            )
            return jsonify({
                'success': True,
                'isRange': True,
                **range_results
            })
        else:
            # Handle single value calculation
            flow_rate = float(flow_rate_data['value'])
            results = []
            for i, geo in enumerate(geometries):
                od = float(geo['od'])
                id = float(geo['id'])
                
                section_name = geo.get('name', '').strip() or f"Section {i + 1}"

                velocity = calculate_annular_velocity(flow_rate, od, id)
                feedback = get_velocity_feedback(velocity)

                results.append({
                    'section': section_name,
                    'od': od,
                    'id': id,
                    'velocity': velocity,
                    **feedback
                })
            
            return jsonify({'success': True, 'isRange': False, 'velocities': results})

    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'error': f"Invalid input: {e}"}), 400
    except Exception as e:
        app.logger.error(f"Annular velocity calculation error: {e}")
        return jsonify({'success': False, 'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
