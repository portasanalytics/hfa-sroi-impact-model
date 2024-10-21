
"""
This script processes survey data to calculate weekly physical activity minutes by multiplying 
activity frequency, session duration, and intensity (based on heart rate). 
It then flags respondents as either active or inactive according to WHO guidelines (150+ minutes of moderate activity or equivalent). 

total mins = frequency x duration x intensity 

"""


import pandas as pd
import numpy as np

# Load the data (updated survey data)
file_path = 'data/survey_data/Elasticity_Questionnaire_v3.xlsx'
sheet_name = 'Data'
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Convert frequency code to days per week
def frequency_to_days(frequency):

    # 0.5 x multiplier for less than a week
    return {1: 0.5, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8}.get(frequency, 0)

# Calculate weekly minutes of activity
def calculate_weekly_minutes(frequency_code, session_minutes):
    days_per_week = frequency_to_days(frequency_code)
    return days_per_week * session_minutes

# Function to classify intensity
def classify_intensity(intensity_code):
    if intensity_code == 1:
        return 'high'
    elif intensity_code == 2:
        return 'moderate'
    else:
        return 'low'

def calculate_activities(row):
    if row['dSEGMENT'] == 1:
        # Gym customers
        q_map = {
            'gym_freq': 'Q4', 'gym_duration': 'Q5r1', 'gym_intensity': 'Q6',
            'walking_freq': 'Q9', 'walking_duration': 'Q10r1', 'walking_intensity': 'Q11',
            'sports_freq': 'Q12', 'sports_duration': 'Q13r1', 'sports_intensity': 'Q14'
        }
    else:
        # Non-gym customers
        q_map = {
            'gym_freq': 'Section_B_Q2', 'gym_duration': 'Section_B_Q3r1', 'gym_intensity': 'Section_B_Q4',
            'walking_freq': 'Section_B_Q7', 'walking_duration': 'Section_B_Q8r1', 'walking_intensity': 'Section_B_Q9',
            'sports_freq': 'Section_B_Q10', 'sports_duration': 'Section_B_Q11r1', 'sports_intensity': 'Section_B_Q12'
        }
    
    # Calculate total gym minutes
    total_gym_minutes = calculate_weekly_minutes(row[q_map['gym_freq']], row[q_map['gym_duration']])
    gym_intensity = classify_intensity(row[q_map['gym_intensity']])
    
    # Walking activity
    walking_minutes = calculate_weekly_minutes(row[q_map['walking_freq']], row[q_map['walking_duration']]) if row[q_map['walking_duration']] >= 10 else 0
    walking_intensity = classify_intensity(row[q_map['walking_intensity']])
    
    # Other sports and physical activities
    other_sports_minutes = calculate_weekly_minutes(row[q_map['sports_freq']], row[q_map['sports_duration']])
    other_sports_intensity = classify_intensity(row[q_map['sports_intensity']])
    
    return pd.Series({
        'total_gym_minutes': total_gym_minutes,
        'gym_intensity': gym_intensity,
        'walking_minutes': walking_minutes,
        'walking_intensity': walking_intensity,
        'other_sports_minutes': other_sports_minutes,
        'other_sports_intensity': other_sports_intensity
    })

# Apply calculations to all respondents
activity_columns = df.apply(calculate_activities, axis=1)
df = pd.concat([df, activity_columns], axis=1)


# Total activity calculation based on intensity
def calculate_total_activity(row):
    total_activity = 0
    
    # Gym activity
    if row['total_gym_minutes'] > 0:
        if row['gym_intensity'] == 'moderate':
            total_activity += row['total_gym_minutes']
        elif row['gym_intensity'] == 'high':
            total_activity += row['total_gym_minutes'] * 2
    
    # Walking activity
    if row['walking_minutes'] > 0:
        if row['walking_intensity'] == 'moderate':
            total_activity += row['walking_minutes']
        elif row['walking_intensity'] == 'high':
            total_activity += row['walking_minutes'] * 2
    
    # Sports activity
    if row['other_sports_minutes'] > 0:
        if row['other_sports_intensity'] == 'moderate':
            total_activity += row['other_sports_minutes']
        elif row['other_sports_intensity'] == 'high':
            total_activity += row['other_sports_minutes'] * 2
    
    return total_activity

# Apply the function to calculate total activity minutes
df['total_activity_mins'] = df.apply(calculate_total_activity, axis=1)

# Apply WHO guidelines to flag active individuals
df['active_flag'] = (df['total_activity_mins'] >= 150).astype(int)

# Select columns to save
output_columns = ['S1', 'dSEGMENT', 'uuid', 'total_activity_mins', 'active_flag',
                 'total_gym_minutes', 'gym_intensity',
                 'walking_minutes', 'walking_intensity',
                 'other_sports_minutes', 'other_sports_intensity']

output_df = df[output_columns]

# Save the activity output
output_file_path = 'data/outputs/activity_output.xlsx'
output_df.to_excel(output_file_path, index=False)

