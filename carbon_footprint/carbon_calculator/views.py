from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from email_validator import validate_email, EmailNotValidError
from .forms import CarbonFootprintForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User


def get_user(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

def create_user(user_data):
    try:
        user = User.objects.create(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            password=user_data["password"]
        )
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def home(request):
    return render(request, 'index.html') 

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def validate_email_address(email):

    import re
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect('login')  # Redirect to login page

        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return redirect('index')  # Redirect to home page after login
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')  # Redirect to login page
    return render(request, 'registration/login.html')

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        # Validate form data
        if not email or not password or not confirm_password:
            messages.error(request, "Email, password, and confirm password are required.")
            return redirect('signup')

        if not validate_email_address(email):
            messages.error(request, "Invalid email format.")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if get_user(email):
            messages.error(request, "This email is already in use.")
            return redirect('signup')

        hashed_password = make_password(password)  # Using Django's built-in password hashing
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": hashed_password
        }

        result = create_user(user_data)

        if 'error' in result:
            messages.error(request, result['error'])
            return redirect('signup')
        else:
            messages.success(request, "Signup successful! Please login.")
            return redirect('login')

    return render(request, 'registration/signup.html')



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
    # Example conversion factors (these should be based on real data)
    conversion_factors = {
        'electricity': {'kWh': 0.249, 'kg': 0},  # Updated conversion factor for electricity
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

            print(f"Electricity: {electricity}, Natural Gas: {natural_gas}, Biomass: {biomass}, Coal: {coal}, Heating Oil: {heating_oil}, LPG: {lpg}")  # Debugging

            return render(request, 'registration/carbon_footprint_result.html', {
                'total_carbon_footprint': total_carbon_footprint,
                'electricity': convert_to_co2e(electricity, units['electricity'], conversion_factors['electricity']),  # Display in whole numbers
                'natural_gas': convert_to_co2e(natural_gas, units['natural_gas'], conversion_factors['natural_gas']),  # Display in whole numbers
                'biomass': convert_to_co2e(biomass, units['biomass'], conversion_factors['biomass']),  # Display in whole numbers
                'coal': convert_to_co2e(coal, units['coal'], conversion_factors['coal']),  # Display in whole numbers
                'heating_oil': convert_to_co2e(heating_oil, units['heating_oil'], conversion_factors['heating_oil']),  # Display in whole numbers
                'lpg': convert_to_co2e(lpg, units['lpg'], conversion_factors['lpg']),# Display in kg CO2e
                'electricity_unit': 'kg CO2e/year',
                'natural_gas_unit': 'kg CO2e/year',
                'biomass_unit': 'kg CO2e/year',
                'coal_unit': 'kg CO2e/year',
                'heating_oil_unit': 'kg CO2e/year',
                'lpg_unit': 'kg CO2e/year',
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CarbonFootprintForm()

    return render(request, 'registration/carbon_footprint_form.html', {'form': form})