from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CarbonFootprintForm, UserRegistrationForm, AirPollutionForm
from .models import DataPoint
import matplotlib.pyplot as plt
import io
import base64
from .models import CarbonFootprintHistory
from django.utils import timezone
from django.contrib.auth import login as auth_login, authenticate
from datetime import timedelta
from datetime import datetime, timedelta
from django.contrib.auth.forms import AuthenticationForm 
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import requests
from django.shortcuts import render
import json
from django.core.files.storage import default_storage
import os

naive_datetime = datetime.now()  # Example naive datetime
aware_datetime = timezone.make_aware(naive_datetime) 

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

def template(request):
    return render(request, 'registration/template.html')

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
    # Define the path to the JSON file
    json_file_path = os.path.join(settings.BASE_DIR, 'carbon_footprint_history.json')

    # Check if the JSON file exists and read the data if available
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = None

    # If data is not available in the file or it's outdated, process and write new data
        # Use timezone-aware datetime
        seven_days_ago = timezone.now() - timedelta(days=7)
        history = CarbonFootprintHistory.objects.filter(user=request.user, created_at__gte=seven_days_ago)

        # Prepare data for the current week
        current_week_data = []
        for record in history:
            total_emission = (record.electricity + record.natural_gas + record.biomass +
                              record.coal + record.heating_oil + record.lpg)
            current_week_data.append({
                'date': record.created_at.strftime('%Y-%m-%d'),
                'total_emission': total_emission
            })

        # Get previous week data (the week before last 7 days)
        previous_week_start = seven_days_ago - timedelta(days=7)
        previous_week_end = seven_days_ago
        previous_history = CarbonFootprintHistory.objects.filter(user=request.user, created_at__range=(previous_week_start, previous_week_end))

        previous_week_data = []
        for record in previous_history:
            total_emission = (record.electricity + record.natural_gas + record.biomass +
                              record.coal + record.heating_oil + record.lpg)
            previous_week_data.append({
                'date': record.created_at.strftime('%Y-%m-%d'),
                'total_emission': total_emission
            })

        # Prepare data for JSON response
        data = {
            'current_week_data': current_week_data,
            'previous_week_data': previous_week_data
        }

        # Write data to JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    # Return data as JSON response
    return JsonResponse(data)

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



def get_air_pollution_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    
    # Debugging: Print the URL to ensure it's correct
    print(f"Pollution API URL: {url}")
    
    response = requests.get(url)
    
    # Debugging: Print the response status code and text
    print(f"Pollution API Response Code: {response.status_code}")
    print(f"Pollution API Response Text: {response.text}")
    
    if response.status_code == 200:
        return response.json()
    return None

def carbon_footprint_api(request):
    if request.method == 'POST':
        form = AirPollutionForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            api_key = '360f90cb3a3ad39295a9cec0ccbd5fe3'
            
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
            
            # Debugging: Print the URL and form data
            print(f"Geocoding API URL: {geo_url}")
            print(f"City: {city}")
            
            geo_response = requests.get(geo_url)
            print(f"Geocoding Response Code: {geo_response.status_code}")
            
            if geo_response.status_code == 200 and geo_response.json():
                geo_data = geo_response.json()[0]
                lat, lon = geo_data['lat'], geo_data['lon']
                
                # Debugging: Print lat and lon
                print(f"Latitude: {lat}, Longitude: {lon}")
                
                pollution_data = get_air_pollution_data(lat, lon, api_key)
                
                if pollution_data:
                    return render(request, 'registration/result.html', {'pollution_data': pollution_data, 'city': city})
                else:
                    print("No pollution data found.")
                    return render(request, 'registration/error.html', {'error': 'Could not retrieve pollution data.'})
            else:
                print("City not found or geocoding failed.")
                return render(request, 'registration/error.html', {'error': 'City not found.'})
    else:
        form = AirPollutionForm()

    return render(request, 'registration/form.html', {'form': form})