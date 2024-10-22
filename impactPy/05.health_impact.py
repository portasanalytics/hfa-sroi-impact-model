
"""
This script calculates health outcomes (cases, deaths, DALYs saved) and cost savings resulting from increased physical activity. 
It uses activity levels, population risk, and relative risk data to estimate the impact of additional active or fairly active adults. 
Functions include reading health data, adjusting risk rates, and calculating cases saved across health conditions. 
Results can be segmented by gender, geography, and activity level. Currently uses gender cut.
"""


import pandas as pd
from health_functions import find_health_outcomes

# Input data
df = pd.read_excel('data/outputs/elasticity_scenarios_gender.xlsx')

# Select only the required columns
df = df[['scenario_id', 'gender', 'newly_active_customers']]

country_map = {
    "SIN": "Singapore",
    "NEW": "Newzealand",
    "SPA": "Spain",
    "NEW": "Newzealand",
    "JAP": "Japan",
    "CAN": "Canada",
    "AUS": "Australia",
    "GER": "Germany",
    "IRE": "Ireland",
    "USA": "America",
    "KSA": "KSA"
}

def get_country_by_code(code):
    """Retrieve country name by code."""
    return country_map.get(code.upper(), "Country code not found")

def process_country(code, df):
    """Process health outcomes for a specific country based on its code."""
    geography = get_country_by_code(code)
    
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
        try:
            adult_health_outcomes = find_health_outcomes(
                additional_active=newly_active,
                additional_fairly_active=newly_fairly_active,
                youth=False, 
                gender=gender,
                geography=geography
            )

            # Add scenario_id, gender, and newly_active_customers to the results
            adult_health_outcomes['scenario_id'] = scenario_id
            adult_health_outcomes['gender'] = gender
            adult_health_outcomes['newly_active_customers'] = newly_active

            col_order = ['scenario_id', 'gender', 'newly_active_customers'] + [col for col in adult_health_outcomes.columns if col not in ['scenario_id', 'gender', 'newly_active_customers']]
            adult_health_outcomes = adult_health_outcomes[col_order]

            # Append the results to the list
            all_results.append(adult_health_outcomes)

        except Exception as e:
            print(f"Error processing scenario {scenario_id} for {geography}: {e}")

    # Combine all results into a single DataFrame if there are results
    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()


with pd.ExcelWriter('health_outcomes.xlsx') as writer:
    # Process each country and save to a separate sheet
    for code in country_map.keys():
        combined_results = process_country(code, df)
        
        # Only write to the Excel sheet if there are results
        if not combined_results.empty:
            combined_results.to_excel(writer, sheet_name=code, index=False)
        else:
            print(f"No results for {code}. Skipping...")

print("All results have been saved to 'health_outcomes.xlsx'")






