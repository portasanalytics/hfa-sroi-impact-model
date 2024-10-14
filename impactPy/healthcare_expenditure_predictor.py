

"""
This script predicts healthcare expenditure for 10 markets for the years 2022 to 2024 based on historical data from the World Bank. 
The healthcare expenditure per capita data, up to 2022, was used to generate predictions for the next two years (2023 and 2024). 

The United Kingdom (UK) data serves as a baseline, allowing us to adjust the cost per case price for other markets. 
However, the UK is not included in the final output, as it was used solely for comparison and normalization purposes.

The prediction model can use two modes:
1. Normal (unweighted) linear regression.
2. Weighted linear regression, where more recent years are given higher importance. 

Key variables:
- `mode`: determines whether the prediction is weighted or unweighted.
- `weight_recent_years`: defines the weight applied to recent years in the weighted mode.
- `num_recent_years`: specifies how many recent years receive this weight.

The final output, excluding the UK, is saved in an Excel file named 'predicted_healthcare_expenditure.xlsx'.
This output serves as input to adjusted_cost_per_case_calculator.py.
"""



import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os

# Load the data
input_file_path = 'data/health_data/input/healthcare_expenditure.xlsx'
df = pd.read_excel(input_file_path, sheet_name="normalised")

def predict_next_years(country_data, years, n_years=3, mode="normal", weight_recent_years=3.0, num_recent_years=3):
    
    """
    Predict the next n_years of data using simple or weighted linear regression.
    """

    # Extract years and values for fitting the model
    historical_years = np.array(years, dtype=int)
    historical_values = pd.to_numeric(country_data[years], errors='coerce').values

    # Reshape data
    historical_years = historical_years.reshape(-1, 1)
    historical_values = historical_values.reshape(-1, 1)
    
    if mode == "weighted":
        # Create weights: higher for the most recent years (e.g., last 3 years)
        weights = np.ones_like(historical_years, dtype=float)
        recent_years_indices = np.where(historical_years >= historical_years[-num_recent_years])[0]
        weights[recent_years_indices] = weight_recent_years  # Apply the specified weight to the recent years
        
        weights = weights.reshape(-1, 1)
    else:
        # No weights for normal mode
        weights = None

    # Train the linear regression model
    model = LinearRegression()
    if weights is None:
        model.fit(historical_years, historical_values)
    else:
        model.fit(historical_years, historical_values, sample_weight=weights.ravel())
    
    # Predict future years
    future_years = np.array(range(2022, 2022 + n_years), dtype=int).reshape(-1, 1)
    predictions = model.predict(future_years)
    
    return predictions.flatten()

# Define the years range
years_range = [str(year) for year in range(2008, 2022)]  # Columns for years 2008 to 2021

# Create a copy of the original dataframe to add predictions
predictions_df = df.copy()

# Add columns for predicted years
for year in range(2022, 2025):
    predictions_df[str(year)] = np.nan

# Loop through each row and apply the prediction model
mode = "weighted"  # Change to "normal" for unweighted mode
weight_recent_years = 3  # Adjust this value to change the emphasis in weighted mode
num_recent_years = 6  # Last X years will get the weight

for index, row in predictions_df.iterrows():
    historical_values = row[years_range]
    predicted_values = predict_next_years(row, years_range, mode=mode, weight_recent_years=weight_recent_years, num_recent_years=num_recent_years)
    
    # Fill in historical values
    for year, value in zip(years_range, historical_values):
        predictions_df.at[index, year] = value
    
    # Fill in predicted values
    for year, value in zip(range(2022, 2025), predicted_values):
        predictions_df.at[index, str(year)] = value

# Save the results
predictions_df=predictions_df[predictions_df['Country Name']!='United Kingdom']
output_dir = os.path.dirname(input_file_path)
output_file_path = os.path.join(output_dir, 'predicted_healthcare_expenditure.xlsx')
predictions_df.to_excel(output_file_path, index=False)

print(f"Predictions have been saved to: {output_file_path}")
