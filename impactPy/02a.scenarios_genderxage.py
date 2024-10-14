
"""
Price Elasticity Model: Analysis for Non-Customers Across 5 Pricing Tiers and 10 Markets

- Load and preprocess survey data, focusing on non-customers (dSEGMENT == 2).
- Define 5 pricing scenarios (10%, 20%, 40%, 60%, 80% discount).
- Apply cumulative response logic: "Yes" for a lower price implies "Yes" for all higher discounts.
- Calculate weighted "Yes" responses for each pricing scenario, segmented by market and gender, using survey weights.
- Merge results with urban population data to estimate potential new customers by market and gender.
- Output scenario results (including new customer estimates) to an Excel file for further analysis.

Calculations are focused only on non-customers who identify price as a barrier.

"""


import pandas as pd 

def load_and_preprocess_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    # Filter for non-customers only
    df = df[df.dSEGMENT == 2]
    
    # Mapping for gender
    gender_mapping = {
        1: "Male",
        2: "Female",
        3: "Others",
        4: "Prefer not to answer"
    }
    df['gender'] = df['S4'].map(gender_mapping)
    
    # Mapping for age groups
    age_mapping = {
        2: "Young Adults (16-35)",
        3: "Young Adults (16-35)",
        4: "Old Adults (>35)",
        5: "Old Adults (>35)",
        6: "Old Adults (>35)",
        7: "Old Adults (>35)"
    }
    df['age_group'] = df['dS3_RECODE'].map(age_mapping)
    
    # Mapping for markets
    market_mapping = {
        1: "Australia", 2: "Canada", 3: "Germany", 4: "Ireland", 5: "Japan",
        6: "KSA (Saudi Arabia)", 7: "New Zealand", 8: "Singapore", 9: "Spain",
        10: "USA (United States of America)"
    }
    df['market'] = df['S1'].map(market_mapping)
    
    return df

def prepare_market_data(df, market_penetration_gender, market_penetration_age, activity_summarised_gender, activity_summarised_age):
    # Create age group versions
    age_group_stats = df.groupby(['market', 'age_group']).agg({
        'WEIGHT': 'sum'
    }).reset_index()
    
    # Calculate total weight per market for age groups
    market_totals = age_group_stats.groupby('market')['WEIGHT'].sum().reset_index()
    age_group_stats = age_group_stats.merge(market_totals, on='market', suffixes=('', '_total'))
    age_group_stats['proportion'] = age_group_stats['WEIGHT'] / age_group_stats['WEIGHT_total']
    
    # Prepare age group market penetration
    age_penetration = []
    
    for market in market_penetration_age['market'].unique():
        market_row = market_penetration_age[market_penetration_age['market'] == market].iloc[0]
        market_stats = age_group_stats[age_group_stats['market'] == market]
        
        for _, age_stat in market_stats.iterrows():
            age_penetration.append({
                'market': market,
                'age_group': age_stat['age_group'],
                'non-customers': market_row['non-customers'] * age_stat['proportion']
            })
    
    age_penetration_df = pd.DataFrame(age_penetration)
    
    # Prepare gender market penetration
    gender_penetration = []
    for market in market_penetration_gender['market'].unique():
        market_rows = market_penetration_gender[market_penetration_gender['market'] == market]
        
        for _, gender_stat in market_rows.iterrows():
            gender_penetration.append({
                'market': market,
                'gender': gender_stat['gender'],
                'non-customers': gender_stat['non-customers']
            })
    
    gender_penetration_df = pd.DataFrame(gender_penetration)


    # Process activity data for age groups using actual age group data
    age_activity = []
    for market in activity_summarised_age['market'].unique():
        market_rows = activity_summarised_age[activity_summarised_age['market'] == market]
        market_stats = age_group_stats[age_group_stats['market'] == market]
        
        for _, age_stat in market_stats.iterrows():
            matching_row = market_rows[market_rows['age_group'] == age_stat['age_group']]
            if not matching_row.empty:
                change = matching_row['change'].iloc[0]
            else:
                change = market_rows['change'].mean()
                
            age_activity.append({
                'market': market,
                'age_group': age_stat['age_group'],
                'change': change
            })
    
    age_activity_df = pd.DataFrame(age_activity)


    # Also need to ensure gender activity data has required columns
    gender_activity = activity_summarised_gender[['market', 'gender', 'change']].copy()
    
    return {
        'gender': {
            'penetration': gender_penetration_df,
            'activity': gender_activity 
        },
        'age_group': {
            'penetration': age_penetration_df,
            'activity': age_activity_df
        }
    }




def calculate_elasticity(df, group_cols, filter_col, valid_values):
    scenarios = ['Q14a', 'Q14b', 'Q14c', 'Q14d', 'Q14e']
    discounts = {'Q14a': '10%', 'Q14b': '20%', 'Q14c': '40%', 'Q14d': '60%', 'Q14e': '80%'}
    
    # Apply cumulative logic
    for i in range(1, len(scenarios)):
        df[scenarios[i]] = df[scenarios[i-1]].where(df[scenarios[i-1]] == 1, df[scenarios[i]])
    
    df['respondent_count'] = 1
    results = []
    
    for scenario in scenarios:
        price = discounts[scenario]
        
        # Only consider responses where price is a barrier (Section_B_Q13r5 is not empty)
        price_barrier_mask = df['Section_B_Q13r5'].notna()
        
        # Calculate weighted yes responses only for those who consider price a barrier
        df['weighted_yes'] = df[scenario].apply(lambda x: 1 if x == 1 else 0) * df['WEIGHT'] * price_barrier_mask
        
        weighted_sums = df.groupby(group_cols).agg(
            total_weight=('WEIGHT', 'sum'),
            weighted_yes=('weighted_yes', 'sum'),
            total_respondents=('respondent_count', 'sum')
        ).reset_index()
        
        # Calculate price barrier stats
        price_barrier_stats = df.groupby(group_cols).agg(
            price_barrier_weight=('WEIGHT', lambda x: (x * price_barrier_mask).sum()),
            non_price_barrier_weight=('WEIGHT', lambda x: (x * ~price_barrier_mask).sum())
        ).reset_index()
        
        # Merge the stats
        weighted_sums = weighted_sums.merge(price_barrier_stats, on=group_cols)
        
        # Calculate percentages
        weighted_sums['% yes'] = (weighted_sums['weighted_yes'] / weighted_sums['price_barrier_weight'])
        weighted_sums['% price_barrier'] = (weighted_sums['price_barrier_weight'] / weighted_sums['total_weight'])
        weighted_sums['% non_price_barrier'] = (weighted_sums['non_price_barrier_weight'] / weighted_sums['total_weight'])
        
        weighted_sums['scenario'] = scenario
        weighted_sums['price'] = price
        
        results.append(weighted_sums[['scenario'] + group_cols + ['price', '% yes', '% price_barrier', '% non_price_barrier', 'total_respondents']])
    
    final_results = pd.concat(results, ignore_index=True)
    final_results = final_results[final_results[filter_col].isin(valid_values)]
    
    return final_results


def process_market_data(final_results, mode, market_data):
    merge_cols = ['market', mode]
    
    # Get the appropriate market data based on mode
    penetration_data = market_data[mode]['penetration']
    activity_data = market_data[mode]['activity']
    
    # Merge the dataframes
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
    
    # Calculate metrics
    merged_df['% yes'] = merged_df['% yes']
    merged_df['new_customers'] = merged_df['non-customers'] * merged_df['% yes'] * merged_df['% price_barrier']
    merged_df['newly_active_customers'] = merged_df['new_customers'] * merged_df['change']
    
    # Create scenario ID
    def create_scenario_id(row):
        if mode == 'gender':
            segment = row['gender'][0]
        else:
            segment = 'Y' if 'Young' in row[mode] else 'O'
        return f"{row['market'][:3].upper()}{row['price'][:2]}{segment}"
    
    merged_df['scenario_id'] = merged_df.apply(create_scenario_id, axis=1)
    
    # Remove duplicates if any exist
    merged_df = merged_df.drop_duplicates()
    
    # Select final columns
    final_df = merged_df[[ 
        'scenario_id',
        'scenario',
        'market',
        'price',
        mode,
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
    file_path = 'data/survey_data/Elasticity_Questionnaire_Latest.xlsx'
    sheet_name = 'Data'
    
    # Load and preprocess data
    df = load_and_preprocess_data(file_path, sheet_name)
    
    # Read market data files
    market_penetration_gender = pd.read_excel('data/inputs/market_penetration_gender.xlsx')
    market_penetration_age = pd.read_excel('data/inputs/market_penetration_age.xlsx')
    activity_summarised_age = pd.read_excel('data/outputs/activity_summarised_age_group.xlsx')
    activity_summarised_gender = pd.read_excel('data/outputs/activity_summarised_gender.xlsx')

    market_data = prepare_market_data(
        df, 
        market_penetration_gender, 
        market_penetration_age, 
        activity_summarised_gender, 
        activity_summarised_age
    )
    
    # Configuration for each mode
    mode_configs = {
        'gender': {
            'group_cols': ['market', 'gender'],
            'filter_col': 'gender', 
            'valid_values': ["Female", "Male"]
        },
        'age_group': {
            'group_cols': ['market', 'age_group'],
            'filter_col': 'age_group', 
            'valid_values': ["Young Adults (16-35)", "Old Adults (>35)"]
        }
    }
    
    # Process each mode and save results
    results = {}
    for mode, config in mode_configs.items():
        # Calculate elasticity
        elasticity_results = calculate_elasticity(
            df,
            config['group_cols'],
            config['filter_col'],
            config['valid_values']
        )
        
        # Process market data
        final_results = process_market_data(
            elasticity_results,
            mode,
            market_data
        )
        
        # Store results
        results[mode] = final_results
        
        # Save to Excel
        output_path = f'data/outputs/elasticity_scenarios_{mode}.xlsx'
        final_results.to_excel(output_path, index=False)
        print(f"Saved {mode} results to {output_path}")
    


if __name__ == "__main__":
    main()