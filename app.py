from flask import Flask, render_template, request, jsonify
import math
import numpy as np
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')

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
        return value * 8.33  # Convert SG to PPG
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

def calculate_bit_hydraulics(flow_rate, mud_density, density_unit, nozzles, bit_size):
    """
    Calculate pressure loss and HSI through a drill bit
    
    Parameters:
    flow_rate (float): Flow rate in gallons per minute (GPM)
    mud_density (float): Mud density in PPG or SG
    density_unit (str): Unit of mud density ('ppg' or 'sg')
    nozzles: list of tuples (size_in_32nds, quantity)
    bit_size (float): Bit size in inches
    
    Returns:
    dict: Pressure loss in PSI and HSI
    """
    # Convert density to PPG if needed
    mud_density_ppg = convert_to_ppg(mud_density, density_unit)
    
    # Calculate total flow area
    total_flow_area = calculate_total_flow_area(nozzles)
    
    # Calculate pressure loss using your formula
    pressure_loss = (mud_density_ppg * flow_rate**2) / (12032 * total_flow_area**2)
    
    # Calculate HSI using your formula
    hsi = (flow_rate * pressure_loss)*1.27 / (1714 * bit_size**2)
    
    return {
        'pressure_loss': round(pressure_loss, 2),
        'hsi': round(hsi, 2),
        'total_flow_area': total_flow_area
    }

def calculate_range_results(min_flow, max_flow, mud_density, density_unit, nozzles, bit_size):
    """
    Calculate results for a range of flow rates in 50 GPM increments
    """
    flow_rates = list(range(int(min_flow), int(max_flow) + 50, 50))
    pressure_losses = []
    hsi_values = []
    
    for flow_rate in flow_rates:
        result = calculate_bit_hydraulics(flow_rate, mud_density, density_unit, nozzles, bit_size)
        pressure_losses.append(result['pressure_loss'])
        hsi_values.append(result['hsi'])
    
    return {
        'flow_rates': flow_rates,
        'pressure_losses': pressure_losses,
        'hsi_values': hsi_values,
        'avg_pressure_loss': round(sum(pressure_losses) / len(pressure_losses), 2),
        'avg_hsi': round(sum(hsi_values) / len(hsi_values), 2)
    }

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
        
        # Calculate total flow area (needed for both single and range calculations)
        total_flow_area = calculate_total_flow_area(nozzles)
        
        if flow_rate_data['isRange']:
            # Calculate results for the range
            range_results = calculate_range_results(
                flow_rate_data['min'],
                flow_rate_data['max'],
                mud_density,
                density_unit,
                nozzles,
                bit_size
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
                nozzles,
                bit_size
            )
            
            return jsonify({
                'success': True,
                **results
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 