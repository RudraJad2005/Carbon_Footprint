from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CarbonFootprintForm, UserRegistrationForm, AirQualityForm
from .models import DataPoint
import matplotlib.pyplot as plt
import io
import base64
from .models import CarbonFootprintHistory
from django.utils import timezone
from django.contrib.auth import login as auth_login, authenticate
from datetime import timedelta
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .utils import load_air_quality_data
import os 
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return render(request, 'index.html') 

def about(request):
    return render(request, 'registration/about.html')

def data_r(request):
    return render(request, 'registration/data_represent.html')

def resources(request):
    return render(request, 'registration/resources.html')

def blog(request):
    return render(request, 'registration/blog.html')

def donate(request):
    return render(request, 'registration/donate.html')

def contact(request):
    return render(request, 'registration/contact.html')

def login(request):
    return render(request, 'registration/login.html')

def sign_up(request):
    return render(request, 'registration/sign_up.html')

def carbon_footprint(request):
    return render(request, 'registration/carbon_form.html')

def carbon_result(request):
    return render(request, 'registration/carbon_result.html')

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
            # Get cleaned data
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


            CarbonFootprintHistory.objects.create(
                user=request.user.username,
                electricity=electricity,
                natural_gas=natural_gas,
                biomass=biomass,
                coal=coal,
                heating_oil=heating_oil,
                lpg=lpg,
                total_co2e=total_carbon_footprint,
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


# Heastory views 

def carbon_footprint_history_view(request):
    # Filter history to include only records from the last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    history = CarbonFootprintHistory.objects.filter(user=request.user, created_at__gte=seven_days_ago)

    # Prepare data for the bar charts
    charts = []
    total_current_week = {
        'Electricity': 0,
        'Natural Gas': 0,
        'Biomass': 0,
        'Coal': 0,
        'Heating Oil': 0,
        'LPG': 0
    }
    
    colors = {
        'Electricity': 'skyblue',
        'Natural Gas': 'lightgreen',
        'Biomass': 'lightcoral',
        'Coal': 'gold',
        'Heating Oil': 'lightpink',
        'LPG': 'lightgray'
    }
    
    for record in history:
        # Aggregate data
        data = {
            'Electricity': record.electricity,
            'Natural Gas': record.natural_gas,
            'Biomass': record.biomass,
            'Coal': record.coal,
            'Heating Oil': record.heating_oil,
            'LPG': record.lpg,
        }
        labels = list(data.keys())
        values = list(data.values())
        bar_colors = [colors[label] for label in labels]

        # Update total for the current week
        for key in total_current_week.keys():
            total_current_week[key] += data.get(key, 0)
        
        # Plotting the bar chart
        plt.figure(figsize=(12, 8))  # Increase the figure size
        plt.bar(labels, values, color=bar_colors)
        plt.xlabel('Emission Type')
        plt.ylabel('CO2 Emission (kg)')
        plt.title(f'Carbon Footprint - {record.created_at.strftime("%Y-%m-%d")}')
        plt.xticks(rotation=45)

        # Convert plot to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')  # Use bbox_inches='tight' to avoid clipping
        buf.seek(0)
        chart_url = base64.b64encode(buf.read()).decode('utf-8')
        charts.append({
            'image_url': f"data:image/png;base64,{chart_url}",
            'date': record.created_at
        })
        plt.close()

    # Get previous period data (for example, the week before the last 7 days)
    previous_week_start = seven_days_ago - timedelta(days=7)
    previous_week_end = seven_days_ago
    previous_history = CarbonFootprintHistory.objects.filter(user=request.user, created_at__range=(previous_week_start, previous_week_end))

    total_previous_week = {
        'Electricity': 0,
        'Natural Gas': 0,
        'Biomass': 0,
        'Coal': 0,
        'Heating Oil': 0,
        'LPG': 0
    }
    
    for record in previous_history:
        data = {
            'Electricity': record.electricity,
            'Natural Gas': record.natural_gas,
            'Biomass': record.biomass,
            'Coal': record.coal,
            'Heating Oil': record.heating_oil,
            'LPG': record.lpg,
        }

        for key in total_previous_week.keys():
            total_previous_week[key] += data.get(key, 0)
    
    # Calculate reduction or increase
    reduction_or_increase = {
        key: total_current_week[key] - total_previous_week.get(key, 0)
        for key in total_current_week
    }
    
    return render(request, 'registration/carbon_footprint_history.html', {
        'charts': charts,
        'total_current_week': total_current_week,
        'reduction_or_increase': reduction_or_increase
    })

# User Login/Signup section

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            user = form.save()
            auth_login(request, user) 
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('carbon_footprint_view')  # Replace 'twitter' with the name of the URL you want to redirect to
        else:
            print("Form is not valid")
            print(form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')  # Redirect to home or another page after login
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def air_quality_view(request):
    form = AirQualityForm()
    data = None

    if request.method == 'POST':
        form = AirQualityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']  # Ensure your form has 'city' field
            date = form.cleaned_data.get('date')  # Use get() for optional fields
            
            # Construct the file path to the CSV file
            file_path = os.path.join(settings.BASE_DIR, 'carbon_calculator', 'data', 'cleaned_air_quality_data.csv')
            
            # Load and filter data
            try:
                df = load_air_quality_data(file_path)
                all_data = df.to_dict(orient='records')  # Convert DataFrame to list of dictionaries
            except FileNotFoundError:
                return HttpResponse("Data file not found.", status=500)
            
            # Check the first entry for debugging
            if all_data:
                print("First entry in the data:", all_data[0])
            
            # Filter data using the correct column name
            data = [entry for entry in all_data if entry.get('city') == city]
            if date:
                data = [entry for entry in data if entry.get('date') == str(date)]

    return render(request, 'registration/air_quality_form.html', {'form': form, 'data': data})
