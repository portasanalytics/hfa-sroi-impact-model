

"""Price Elasticity for income group"""

import pandas as pd
import numpy as np

def load_and_preprocess_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Filter for non-customers - only non customers respond to price discounts
    df = df[df.dSEGMENT == 2]
    
    # Mapping for markets
    market_mapping = {
        1: "Australia", 2: "Canada", 3: "Germany", 4: "Ireland", 5: "Japan",
        6: "KSA (Saudi Arabia)", 7: "New Zealand", 8: "Singapore", 9: "Spain",
        10: "USA (United States of America)"
    }
    df['market'] = df['S1'].map(market_mapping)

    # Income level mapping
    column_mapping = {
        1: "AU", 2: "CA", 3: "DE", 4: "IE", 5: "JP",
        6: "SA", 7: "NZ", 8: "SG", 9: "ES", 10: "US"
    }

    def map_income_level(row):
        market = row['S1']
        income_column = f'S5_{column_mapping[market]}'
        income_value = row[income_column]
        
        if income_value == 99:
            return 'Prefer not to answer'
        
        income_mappings = {
            1: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Australia
            2: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Canada
            3: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'High'},  # Germany
            4: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Ireland
            5: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'High', 6: 'High'},  # Japan
            6: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # Saudi Arabia
            7: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'},  # New Zealand
            8: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'High', 6: 'High'},  # Singapore
            9: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'High', 7: 'High', 8: 'High'},  # Spain
            10: {1: 'Low', 2: 'Middle', 3: 'Middle', 4: 'Middle', 5: 'Middle', 6: 'Middle', 7: 'High', 8: 'High'}  # USA
        }
        
        return income_mappings.get(market, {}).get(income_value, 'Unknown')

    df['income_level'] = df.apply(map_income_level, axis=1)

    return df

def calculate_elasticity(df, group_cols, filter_col, valid_values):
    scenarios = ['Q14a', 'Q14b', 'Q14c', 'Q14d', 'Q14e']
    discounts = {'Q14a': '10%', 'Q14b': '20%', 'Q14c': '40%', 'Q14d': '60%', 'Q14e': '80%'}
    
    for i in range(1, len(scenarios)):
        df[scenarios[i]] = df[scenarios[i-1]].where(df[scenarios[i-1]] == 1, df[scenarios[i]])
    
    df['respondent_count'] = 1
    results = []
    
    for scenario in scenarios:
        price = discounts[scenario]
        
        price_barrier_mask = df['Section_B_Q13r5'].notna()
        df['weighted_yes'] = df[scenario].apply(lambda x: 1 if x == 1 else 0) * df['WEIGHT'] * price_barrier_mask
        
        weighted_sums = df.groupby(group_cols).agg(
            total_weight=('WEIGHT', 'sum'),
            weighted_yes=('weighted_yes', 'sum'),
            total_respondents=('respondent_count', 'sum')
        ).reset_index()
        
        price_barrier_stats = df.groupby(group_cols).agg(
            price_barrier_weight=('WEIGHT', lambda x: (x * price_barrier_mask).sum()),
            non_price_barrier_weight=('WEIGHT', lambda x: (x * ~price_barrier_mask).sum())
        ).reset_index()
        
        weighted_sums = weighted_sums.merge(price_barrier_stats, on=group_cols)
        
        weighted_sums['% yes'] = (weighted_sums['weighted_yes'] / weighted_sums['price_barrier_weight'])
        weighted_sums['% price_barrier'] = (weighted_sums['price_barrier_weight'] / weighted_sums['total_weight'])
        weighted_sums['% non_price_barrier'] = (weighted_sums['non_price_barrier_weight'] / weighted_sums['total_weight'])
        
        weighted_sums['scenario'] = scenario
        weighted_sums['price'] = price
        
        results.append(weighted_sums[['scenario'] + group_cols + ['price', '% yes', '% price_barrier', '% non_price_barrier', 'total_respondents']])
    
    final_results = pd.concat(results, ignore_index=True)
    final_results = final_results[final_results[filter_col].isin(valid_values)]
    
    return final_results

def process_market_data(final_results, market_data):
    merge_cols = ['market', 'income_level']
    
    penetration_data = market_data['penetration']
    activity_data = market_data['activity']
    
    merged_df = pd.merge(
        final_results,
        penetration_data[merge_cols + ['non-customers']],
        on=merge_cols,
        how='left'
    )
    
    merged_df = pd.merge(
        merged_df,
        activity_data[merge_cols + ['change']],
        on=merge_cols,
        how='left'
    )
    
    merged_df['new_customers'] = merged_df['non-customers'] * merged_df['% yes'] * merged_df['% price_barrier']
    merged_df['newly_active_customers'] = merged_df['new_customers'] * merged_df['change']
    
    def create_scenario_id(row):
        income_level = row['income_level'][0].upper()
        return f"{row['market'][:3].upper()}{row['price'][:2]}{income_level}"
    
    merged_df['scenario_id'] = merged_df.apply(create_scenario_id, axis=1)
    
    merged_df = merged_df.drop_duplicates()
    
    final_df = merged_df[[ 
        'scenario_id',
        'scenario',
        'market',
        'price',
        'income_level',
        'non-customers',
        '% yes',
        '% price_barrier',
        '% non_price_barrier',
        'new_customers',
        'change',
        'newly_active_customers'
    ]]
    
    return final_df

def main():
    # File paths
    file_path = 'data/survey_data/Elasticity_Questionnaire_v3.xlsx'
    sheet_name = 'Data'
    
    # Load and preprocess data
    df = load_and_preprocess_data(file_path, sheet_name)
    
    # Read market data files
    market_penetration_income = pd.read_excel('data/inputs/market_penetration_income.xlsx')
    activity_summarised_income = pd.read_excel('data/outputs/activity_summarised_income_level.xlsx')

    market_data = {
        'penetration': market_penetration_income,
        'activity': activity_summarised_income
    }
    
    # Configuration for income mode
    mode_config = {
        'group_cols': ['market', 'income_level'],
        'filter_col': 'income_level', 
        'valid_values': ["Low", "Middle", "High"]
    }
    
    # Calculate elasticity
    elasticity_results = calculate_elasticity(
        df,
        mode_config['group_cols'],
        mode_config['filter_col'],
        mode_config['valid_values']
    )
    
    # Process market data
    final_results = process_market_data(elasticity_results, market_data)
    
    # Save results
    output_path = 'data/outputs/elasticity_scenarios_income.xlsx'
    final_results.to_excel(output_path, index=False)
    print(f"Saved income results to {output_path}")

if __name__ == "__main__":
    main()