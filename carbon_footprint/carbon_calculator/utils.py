# utils.py
import pandas as pd
from django.conf import settings
import os

def load_air_quality_data(file_path):
    df = pd.read_csv(file_path)
    return df

# def preprocess_csv(input_file, output_file):
#     # Load the CSV file, skipping the header rows until the actual data starts
#     df = pd.read_csv(input_file, skiprows=5)

#     # Rename columns if necessary
#     df.columns = ['S.No.', 'State', 'City', 'Station Name', 'Current AQI value']

#     # Save the cleaned data to a new CSV file
#     df.to_csv(output_file, index=False)

# # Example usage
# input_file = 'C:/Users/SVI/OneDrive/Desktop/Carbon_FootPrint/carbon_footprint/carbon_calculator/data_set.csv'
# output_file = 'C:/Users/SVI/OneDrive/Desktop/Carbon_FootPrint/carbon_footprint/carbon_calculator/cleaned_air_quality_data.csv'
# preprocess_csv(input_file, output_file)