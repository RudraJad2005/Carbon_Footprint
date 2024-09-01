from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CarbonFootprintForm
from .models import DataPoint
import matplotlib.pyplot as plt
import io
import base64

def home(request):
    return render(request, 'index.html') 

def about(request):
    return render(request, 'registration/about.html')

def data_r(request):
    return render(request, 'registration/data_represent.html')

def resources(request):
    return render(request, 'registration/resources.html')

def convert_to_co2e(value, unit, conversion_factor):
    """
    Converts the given value to CO2e using the specified conversion factor.
    """
    if unit in conversion_factor:
        return round(value * conversion_factor[unit])
    return 0

def calculate_carbon_footprint(electricity, natural_gas, biomass, coal, heating_oil, lpg, units, conversion_factors):
    """
    Calculate the total carbon footprint based on the given energy sources and units.
    """
    total_co2e = 0

    # Convert each energy source to CO2e
    total_co2e += convert_to_co2e(electricity, units['electricity'], conversion_factors['electricity'])
    total_co2e += convert_to_co2e(natural_gas, units['natural_gas'], conversion_factors['natural_gas'])
    total_co2e += convert_to_co2e(biomass, units['biomass'], conversion_factors['biomass'])
    total_co2e += convert_to_co2e(coal, units['coal'], conversion_factors['coal'])
    total_co2e += convert_to_co2e(heating_oil, units['heating_oil'], conversion_factors['heating_oil'])
    total_co2e += convert_to_co2e(lpg, units['lpg'], conversion_factors['lpg'])

    return total_co2e

def carbon_footprint_view(request):
    # Example conversion factors
    conversion_factors = {
        'electricity': {'kWh': 0.249, 'kg': 0},
        'natural_gas': {'kWh': 0.185, 'kg': 2.75},
        'biomass': {'kWh': 0.039, 'kg': 0.015},
        'coal': {'kWh': 0.341, 'kg': 2.42},
        'heating_oil': {'kWh': 0.265, 'kg': 2.68, 'liters': 2.52},
        'lpg': {'kWh': 0.214, 'kg': 1.51, 'liters': 1.52},
    }

    if request.method == 'POST':
        form = CarbonFootprintForm(request.POST)
        if form.is_valid():
            electricity = form.cleaned_data['electricity'] or 0
            natural_gas = form.cleaned_data['natural_gas'] or 0
            biomass = form.cleaned_data['biomass'] or 0
            coal = form.cleaned_data['coal'] or 0
            heating_oil = form.cleaned_data['heating_oil'] or 0
            lpg = form.cleaned_data['lpg'] or 0

            units = {
                'electricity': form.cleaned_data['electricity_unit'],
                'natural_gas': form.cleaned_data['natural_gas_unit'],
                'biomass': form.cleaned_data['biomass_unit'],
                'coal': form.cleaned_data['coal_unit'],
                'heating_oil': form.cleaned_data['heating_oil_unit'],
                'lpg': form.cleaned_data['lpg_unit'],
            }

            total_carbon_footprint = calculate_carbon_footprint(
                electricity, natural_gas, biomass, coal, heating_oil, lpg, units, conversion_factors
            )

            # Store the data in session
            request.session['carbon_data'] = {
                'electricity': electricity,
                'natural_gas': natural_gas,
                'biomass': biomass,
                'coal': coal,
                'heating_oil': heating_oil,
                'lpg': lpg,
                'units': units
            }

            return redirect('data_represent')  # Corrected redirection
    else:
        form = CarbonFootprintForm()

    return render(request, 'registration/carbon_footprint_form.html', {'form': form})

def insert_data(request):
    if request.method == 'POST':
        label = request.POST['label']
        value = request.POST['value']
        DataPoint.objects.create(label=label, value=value)
        return redirect('visualize_data')

    return render(request, 'insert_data.html')

def visualize_data(request):
    data = DataPoint.objects.all()

    # Data preparation for Matplotlib
    labels = [d.label for d in data]
    values = [d.value for d in data]

    # Plotting the data using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color='blue')
    plt.xlabel('Labels')
    plt.ylabel('Values')
    plt.title('Data Visualization')

    # Convert plot to PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')  # Ensure decode to string
    uri = f"data:image/png;base64,{string}"

    return render(request, 'visualize_data.html', {'data': data, 'chart': uri})

def generate_carbon_chart(carbon_data):
    conversion_factors = {
        'electricity': {'kWh': 0.249, 'kg': 0},
        'natural_gas': {'kWh': 0.185, 'kg': 2.75},
        'biomass': {'kWh': 0.039, 'kg': 0.015},
        'coal': {'kWh': 0.341, 'kg': 2.42},
        'heating_oil': {'kWh': 0.265, 'kg': 2.68, 'liters': 2.52},
        'lpg': {'kWh': 0.214, 'kg': 1.51, 'liters': 1.52},
    }

    units = carbon_data['units']
    labels = ['Electricity', 'Natural Gas', 'Biomass', 'Coal', 'Heating Oil', 'LPG']
    values = [
        convert_to_co2e(carbon_data['electricity'], units['electricity'], conversion_factors['electricity']),
        convert_to_co2e(carbon_data['natural_gas'], units['natural_gas'], conversion_factors['natural_gas']),
        convert_to_co2e(carbon_data['biomass'], units['biomass'], conversion_factors['biomass']),
        convert_to_co2e(carbon_data['coal'], units['coal'], conversion_factors['coal']),
        convert_to_co2e(carbon_data['heating_oil'], units['heating_oil'], conversion_factors['heating_oil']),
        convert_to_co2e(carbon_data['lpg'], units['lpg'], conversion_factors['lpg'])
    ]

    # Define colors
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6']

    plt.figure(figsize=(10, 10))
    plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Carbon Footprint by Energy Source')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    uri = f"data:image/png;base64,{string}"
    return uri


def data_r(request):
    carbon_data = request.session.get('carbon_data', None)
    chart_uri = None

    if carbon_data:
        chart_uri = generate_carbon_chart(carbon_data)
        # Prepare data for the table
        data_for_table = {
            'electricity': carbon_data['electricity'],
            'natural_gas': carbon_data['natural_gas'],
            'biomass': carbon_data['biomass'],
            'coal': carbon_data['coal'],
            'heating_oil': carbon_data['heating_oil'],
            'lpg': carbon_data['lpg'],
            'total_carbon_footprint': calculate_carbon_footprint(
                carbon_data['electricity'], carbon_data['natural_gas'], carbon_data['biomass'],
                carbon_data['coal'], carbon_data['heating_oil'], carbon_data['lpg'],
                carbon_data['units'], {
                    'electricity': {'kWh': 0.249, 'kg': 0},
                    'natural_gas': {'kWh': 0.185, 'kg': 2.75},
                    'biomass': {'kWh': 0.039, 'kg': 0.015},
                    'coal': {'kWh': 0.341, 'kg': 2.42},
                    'heating_oil': {'kWh': 0.265, 'kg': 2.68, 'liters': 2.52},
                    'lpg': {'kWh': 0.214, 'kg': 1.51, 'liters': 1.52},
                }
            )
        }

    return render(request, 'registration/data_represent.html', {'chart': chart_uri, 'data': data_for_table})
