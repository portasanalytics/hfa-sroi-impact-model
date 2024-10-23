import pandas as pd

def calculate_adjusted_risk_rates(PopulationRisk, PopulationActiveRate, RelativeRisk, PopulationFairlyActiveRate=None, FairlyActiveRelativeRisk=None):


    if PopulationFairlyActiveRate is None:

        ActiveRisk = PopulationRisk/(RelativeRisk * (1 - PopulationActiveRate) + PopulationActiveRate)

        InactiveRisk = ActiveRisk * RelativeRisk

        return ActiveRisk, InactiveRisk
    
    else:

        InactiveRisk = PopulationRisk/((1 - PopulationActiveRate - PopulationFairlyActiveRate) + (PopulationActiveRate * (1 / RelativeRisk)) + (PopulationFairlyActiveRate * (1/FairlyActiveRelativeRisk)))

        ActiveRisk = InactiveRisk / RelativeRisk

        FairlyActiveRisk = InactiveRisk / FairlyActiveRelativeRisk

        return ActiveRisk, FairlyActiveRisk, InactiveRisk

def calculate_cases_saved(ActiveRisk, InactiveRisk, ActiveNum):

    ActiveAffected = ActiveRisk * ActiveNum

    InactiveAffected = InactiveRisk * ActiveNum

    CasesSaved = InactiveAffected - ActiveAffected

    return CasesSaved


def read_relative_risks(source, factor, age_group, gender, geography, activity_level = 'active', local = False):

    if local:
        risks_df = pd.read_csv(source)
    
    filtered_df = risks_df[(risks_df['factor'] == factor) & (risks_df['age_group'] == age_group) & (risks_df['activity_level'] == activity_level)].reset_index()

    if len(filtered_df[(filtered_df['gender'] == gender)].index) > 0:
        filtered_df = filtered_df[(filtered_df['gender'] == gender)].reset_index()

    elif len(filtered_df[(filtered_df['gender'] == "all")].index) > 0:
        filtered_df = filtered_df[(filtered_df['gender'] == "all")].reset_index()
    
    else:
        print("Using assumptions from opposite gender for relative risk")

    if len(filtered_df[(filtered_df['geography'] == geography)].index) > 0:
        filtered_df = filtered_df[(filtered_df['geography'] == geography)]
    
    elif len(filtered_df[(filtered_df['geography'] == "global")].index) > 0:
        filtered_df = filtered_df[(filtered_df['geography'] == "global")]

        print("Using global assumptions (not region-specific) for relative risk")
    
    else:
        filtered_df = filtered_df.head(1)

        print(f"Using geography data from {filtered_df['geography'].values} for relative risk")

    return filtered_df

def read_cost_per_case(source, factor, age_group, gender, geography, direct = True, local = False):

    if local:
        costs_df = pd.read_csv(source)
    
    filtered_df = costs_df[(costs_df['factor'] == factor) & (costs_df['age_group'] == age_group) & (costs_df['direct'] == direct)].reset_index()

    if len(filtered_df[(filtered_df['gender'] == gender)].index) > 0:
        filtered_df = filtered_df[(filtered_df['gender'] == gender)].reset_index()

    elif len(filtered_df[(filtered_df['gender'] == "all")].index) > 0:
        filtered_df = filtered_df[(filtered_df['gender'] == "all")].reset_index()
    
    else:
        print("Using assumptions from opposite gender for cost per case")

    if len(filtered_df[(filtered_df['geography'] == geography)].index) > 0:
        filtered_df = filtered_df[(filtered_df['geography'] == geography)]
    
    elif len(filtered_df[(filtered_df['geography'] == "global")].index) > 0:
        filtered_df = filtered_df[(filtered_df['geography'] == "global")]

        print("Using global assumptions (not region-specific) for cost per case")
    
    else:
        filtered_df = filtered_df.head(1)

        print(f"Using geography data from {filtered_df['geography'].values} for cost per case")

    return filtered_df


def read_population_risks(source, factor, age_group, gender, geography, local = False):

    if local:
        risks_df = pd.read_csv(source)

    filtered_df = risks_df[(risks_df['factor'] == factor) & (risks_df['age_group'] == age_group)].reset_index()

    if len(filtered_df[(filtered_df['gender'] == gender)].index) > 0:
        filtered_df = filtered_df[(filtered_df['gender'] == gender)].reset_index()

    elif len(filtered_df[(filtered_df['gender'] == "all")].index) > 0:
        filtered_df = filtered_df[(filtered_df['gender'] == "all")].reset_index()
    
    else:
        print("Using assumptions from opposite gender for population risks")

    if len(filtered_df[(filtered_df['geography'] == geography)].index) > 0:
        filtered_df = filtered_df[(filtered_df['geography'] == geography)]
    
    elif len(filtered_df[(filtered_df['geography'] == "global")].index) > 0:
        filtered_df = filtered_df[(filtered_df['geography'] == "global")]

        print("Using global assumptions (not region-specific) for population risks")
    
    else:
        filtered_df = filtered_df.head(1)

        print(f"Using geography data from {filtered_df['geography'].values} for population risks")

    return filtered_df




def read_activity_levels(source,age_group,gender, geography, activity_level='active', local=False):

    if local:
        activity_df = pd.read_csv(source)
    else:
        activity_df = pd.DataFrame()

    filtered_df = activity_df[(activity_df['age_group'] == age_group) & 
                              (activity_df['gender'] == gender) & 
                              (activity_df['geography'] == geography) & 
                              (activity_df['activity_level'] == activity_level)]

    if filtered_df.empty:
        raise ValueError(f"No data found for the provided filters: age_group={age_group}, gender={gender}, geography={geography}, activity_level={activity_level}")

    return filtered_df.reset_index(drop=True)





def find_health_outcomes(additional_active, 
                         additional_fairly_active, 
                         youth=False,
                         health_list=['coronary heart disease', 
                                      'anxiety',
                                      'depression',
                                      'stroke',
                                      'diabetes (type 2)',
                                      'breast cancer',
                                      'endometrial uterine cancer',
                                      'colon cancer',
                                      'alzheimer and other dementia',
                                      'osteoporosis'],
                         youth_health_list=['anxiety', 'depression', 'obesity'],
                         gender='female',
                         geography='global'):

    cases_saved_list = []

    if youth:
        pass
    else:
        affected_pop = additional_active
        fairly_affected_pop = additional_fairly_active

    # Get market specific activity data
    activity_df = read_activity_levels(age_group='adult', gender=gender, geography=geography, source='data/health_data/activity_levels.csv', local=True)

    # Use England data for fairly active levels if market-specific data is not available
    fairly_activity_df = read_activity_levels(age_group='adult', gender=gender, geography='england', activity_level='fairly active', source='data/health_data/activity_levels.csv', local=True)

    for h in health_list:
        print(h)

        # Use global or UK data for relative risks
        risks_df = read_relative_risks(factor=h, age_group='adult', gender=gender, geography='england', source='data/health_data/relative_risks.csv', local=True)
        fairly_risks_df = read_relative_risks(factor=h, age_group='adult', gender=gender, geography='england', activity_level='fairly active', source='data/health_data/relative_risks.csv', local=True)

        # Use market-specific data for population risks
        pop_df = read_population_risks(factor=h, age_group='adult', gender=gender, geography=geography, source='data/health_data/population_risks.csv', local=True)

        # Use global data for mortality risks and DALYs
        pop_deaths_df = read_population_risks(factor=h, age_group='adult', gender=gender, geography='global', source='data/health_data/population_mortality_risks.csv', local=True)
        pop_dalys_df = read_population_risks(factor=h, age_group='adult', gender=gender, geography='global', source='data/health_data/population_dalys.csv', local=True)

        


        # Calculate adjusted risk rates
        a, b, c = calculate_adjusted_risk_rates(
            pop_df['population_rate'].iloc[0] / pop_df['rate_per'].iloc[0],
            activity_df['activity_rate'].values[0],
            risks_df['relative_risk'].iloc[0],
            fairly_activity_df['activity_rate'].iloc[0],
            fairly_risks_df['relative_risk'].iloc[0]
        )

        a_daly, b_daly, c_daly = calculate_adjusted_risk_rates(
            pop_dalys_df['population_rate'].iloc[0] / pop_dalys_df['rate_per'].iloc[0],
            activity_df['activity_rate'].values[0],
            risks_df['relative_risk'].iloc[0],
            fairly_activity_df['activity_rate'].iloc[0],
            fairly_risks_df['relative_risk'].iloc[0]
        )

        a_d, b_d, c_d = calculate_adjusted_risk_rates(
            pop_deaths_df['population_rate'].iloc[0] / pop_deaths_df['rate_per'].iloc[0],
            activity_df['activity_rate'].values[0],
            risks_df['relative_risk'].iloc[0],
            fairly_activity_df['activity_rate'].iloc[0],
            fairly_risks_df['relative_risk'].iloc[0]
        )

        # Use market-specific data for cost per case if available, otherwise use global
        cost_per_case = read_cost_per_case(factor=h, age_group='adult', gender='all', geography=geography, source='data/health_data/cost_per_case_adjusted.csv', local=True)
        indirect_cost_per_case = read_cost_per_case(factor=h, age_group='adult', gender='all', geography=geography, direct=False, source='data/health_data/cost_per_case_adjusted.csv', local=True)

        # Calculate cases, deaths, and DALYs saved
        cases_saved, fairly_cases_saved = calculate_cases_saved(a, c, affected_pop), calculate_cases_saved(b, c, fairly_affected_pop)
        deaths_saved, fairly_deaths_saved = calculate_cases_saved(a_d, c_d, affected_pop), calculate_cases_saved(b_d, c_d, fairly_affected_pop)
        dalys_saved, fairly_dalys_saved = calculate_cases_saved(a_daly, c_daly, affected_pop), calculate_cases_saved(b_daly, c_daly, fairly_affected_pop)


        # Print the input data for activity levels, population risk, cost per case, and relative risk
        print(f"Input Data for {geography}, disease {h} and gender {gender}:")
        print(f"Population Risk: {pop_df['population_rate'].iloc[0]}")
        print(f"Activity Rate: {activity_df['activity_rate'].values[0]}")
        print(f"Relative Risk: {risks_df['relative_risk'].iloc[0]}")
        print(f"Cost per case: {cost_per_case.iloc[0,14]}\n")



        cases_saved_dict = {
            'factor': h,
            'risk_active': a,
            'risk_inactive': c,
            'active_cases_saved': cases_saved,
            'active_dalys_saved': dalys_saved,
            'active_deaths_saved': deaths_saved,
            'direct_cost_per_case': cost_per_case.iloc[0, 14],
            'direct_cost_saving': (fairly_cases_saved + cases_saved) * cost_per_case.iloc[0, 14],
            'indirect_cost_per_case': indirect_cost_per_case.iloc[0, 14],
            'indirect_cost_saving': (fairly_cases_saved + cases_saved) * indirect_cost_per_case.iloc[0, 14],
            'total_saving': (fairly_cases_saved + cases_saved) * (cost_per_case.iloc[0, 14] + indirect_cost_per_case.iloc[0, 14])
        }

        cases_saved_list.append(cases_saved_dict)

    cases_saved_df = pd.DataFrame(cases_saved_list)
    youth_cases_saved_df = pd.DataFrame()

    if youth:
        youth_cases_saved_df = pd.DataFrame()

    return cases_saved_df