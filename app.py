from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Pricing constants (adjust these based on your market)
PAINT_PRICES = {
    'basic': 35,      # per gallon
    'premium': 55,    # per gallon
    'luxury': 75      # per gallon
}

LABOR_RATES = {
    'basic': 2.5,     # per sq ft
    'premium': 3.5,   # per sq ft  
    'luxury': 4.5     # per sq ft
}

def calculate_estimate(data):
    # Extract form data
    length = float(data.get('length', 0))
    width = float(data.get('width', 0))
    height = float(data.get('height', 0))
    doors = int(data.get('doors', 0))
    windows = int(data.get('windows', 0))
    condition = data.get('condition', 'good')
    paint_quality = data.get('paint_quality', 'basic')
    coats = int(data.get('coats', 2))
    
    # Calculate areas
    wall_area = 2 * (length * height) + 2 * (width * height)
    door_area = doors * 20  # average door = 20 sq ft
    window_area = windows * 12  # average window = 12 sq ft
    paintable_area = wall_area - door_area - window_area
    
    # Condition multipliers for prep work
    prep_multipliers = {
        'excellent': 1.0,
        'good': 1.2, 
        'fair': 1.5,
        'poor': 2.0
    }
    
    # Calculate materials
    coverage_per_gallon = 350  # sq ft per gallon
    gallons_needed = (paintable_area * coats) / coverage_per_gallon
    gallons_needed = max(1, round(gallons_needed + 0.5))  # Round up, minimum 1 gallon
    
    paint_cost = gallons_needed * PAINT_PRICES[paint_quality]
    
    # Supplies (brushes, rollers, drop cloths, etc.)
    supplies_cost = paintable_area * 0.15
    
    # Labor calculation
    base_labor_cost = paintable_area * LABOR_RATES[paint_quality]
    prep_multiplier = prep_multipliers[condition]
    total_labor = base_labor_cost * prep_multiplier
    
    # Estimated hours
    hours = paintable_area / 150 * prep_multiplier  # base: 150 sq ft per hour
    
    # Totals
    materials_total = paint_cost + supplies_cost
    subtotal = materials_total + total_labor
    markup = subtotal * 0.20  # 20% markup
    total = subtotal + markup
    
    return {
        'room_info': {
            'length': length,
            'width': width, 
            'height': height,
            'doors': doors,
            'windows': windows,
            'wall_area': round(wall_area, 1),
            'paintable_area': round(paintable_area, 1)
        },
        'materials': {
            'gallons_needed': gallons_needed,
            'paint_cost': round(paint_cost, 2),
            'supplies_cost': round(supplies_cost, 2),
            'materials_total': round(materials_total, 2)
        },
        'labor': {
            'hours': round(hours, 1),
            'labor_cost': round(total_labor, 2)
        },
        'totals': {
            'subtotal': round(subtotal, 2),
            'markup': round(markup, 2),
            'total': round(total, 2)
        },
        'job_details': {
            'condition': condition,
            'paint_quality': paint_quality,
            'coats': coats,
            'date': datetime.now().strftime('%B %d, %Y')
        }
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get customer info
        customer_name = request.form.get('customer_name', 'Customer')
        customer_email = request.form.get('customer_email', '')
        customer_phone = request.form.get('customer_phone', '')
        job_address = request.form.get('job_address', '')
        
        # Calculate estimate
        estimate = calculate_estimate(request.form)
        
        # Display results on web page instead of PDF for now
        return render_template('estimate.html', 
                             estimate=estimate,
                             customer_name=customer_name,
                             customer_email=customer_email,
                             customer_phone=customer_phone,
                             job_address=job_address)
    
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)