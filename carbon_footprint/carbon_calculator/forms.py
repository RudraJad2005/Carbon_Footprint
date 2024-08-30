from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class CarbonFootprintForm(forms.Form):
    electricity = forms.FloatField(label='Electricity (kWh or kg)', required=False)
    natural_gas = forms.FloatField(label='Natural Gas (kWh or kg)', required=False)
    biomass = forms.FloatField(label='Biomass (kWh or kg)', required=False)
    coal = forms.FloatField(label='Coal (kWh or kg)', required=False)
    heating_oil = forms.FloatField(label='Heating Oil (kWh, kg, or liters)', required=False)
    lpg = forms.FloatField(label='LPG (kWh, kg, or liters)', required=False)

    electricity_unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('kg', 'kg')], required=False)
    natural_gas_unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('kg', 'kg')], required=False)
    biomass_unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('kg', 'kg')], required=False)
    coal_unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('kg', 'kg')], required=False)
    heating_oil_unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('kg', 'kg'), ('liters', 'liters')], required=False)
    lpg_unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('kg', 'kg'), ('liters', 'liters')], required=False)
