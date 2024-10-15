"""
This script calculates health outcomes (cases, deaths, DALYs saved) and cost savings resulting from increased physical activity. 
It uses activity levels, population risk, and relative risk data to estimate the impact of additional active or fairly active adults. 
Functions include reading health data, adjusting risk rates, and calculating cases saved across health conditions. 
Results can be segmented by gender, geography, and activity level. Currently uses gender cut.
"""



from health_functions import find_health_outcomes
import pandas as pd

# Input data
df = pd.read_excel('data/outputs/elasticity_scenarios_gender.xlsx')

# Select only the required columns
df = df[['scenario_id', 'gender', 'newly_active_customers']]

# Manually specify the market code here
code = "USA"

# Filter data for the specified market
market_df = df[df['scenario_id'].str.startswith(code)]

all_results = []

# Loop through each row and calculate health outcomes
for index, row in market_df.iterrows():
    scenario_id = row['scenario_id']
    gender = row['gender'].lower()
    newly_active = row['newly_active_customers']
    newly_fairly_active = 0

    # Call the find_health_outcomes function
    adult_health_outcomes, youth_health_outcomes = find_health_outcomes(
        additional_active=newly_active,
        additional_fairly_active=newly_fairly_active,
        youth=False, 
        gender=gender
    )

    # Add scenario_id, gender, and newly_active_customers to the results
    adult_health_outcomes['scenario_id'] = scenario_id
    adult_health_outcomes['gender'] = gender
    adult_health_outcomes['newly_active_customers'] = newly_active

    # Append the results to the list
    all_results.append(adult_health_outcomes)

# Combine all results into a single DataFrame
combined_results = pd.concat(all_results, ignore_index=True)

# Save the combined results to a single Excel file
filename = f'combined_health_outcomes_{code}.xlsx'
combined_results.to_excel(filename, index=False)

print(f"All results for market {code} have been saved to '{filename}'")