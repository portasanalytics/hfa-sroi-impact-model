import pandas as pd


# def find_additional_active_adults(active_youth, 
#                                   gender = 'all',
#                                   geography = 'global',
#                                   activity_source = 'data/health_data/activity_levels.csv', 
#                                   relative_risk_source = 'data/health_data/relative_risks.csv',
#                                   local = True):
#     """
#     Calculate the expected number of active adults who will come from a group of active children.

#     The first step is to calculate the likelihood of being an active adult for active children and for inactive children. This follows the standard methodology of solving for these 
#     rates based on the population risk, the relative risk for active vs inactive children, the share of the population who are active, and the share of the population who are inactive.

#     The second step is to then take the number of active children and work out the additional number of active adults we can expect from this group over and above those who would 
#     have become active adults despite being inactive as a child. This is calculated by multiplying the likelihood of being an active adult for an active child by the number of 
#     active children to give the expected number of active adults. Then subtracting the expected number of active adults had the group of children remained inactive (calculated by multiplying
#     the chance of being an active adult for an inactive child by the number of children in the group).

#     Args:
#         active_youth (float): Number of newly/additionally active children.
#         gender (str, optional): Gender of the population ('all', 'male', 'female'). Defaults to 'all'.
#         geography (str, optional): Geographic region ('global', 'england', etc.). Defaults to 'global'.
#         activity_source (str, optional): Path to the activity levels data file. Defaults to 'data/activity_levels.csv'.
#         relative_risk_source (str, optional): Path to the relative risks data file. Defaults to 'data/relative_risks.csv'.
#         local (bool, optional): Whether to use local data files. Defaults to True.

#     Returns:
#         float: The expected number of additionally active adults that will result from the group of newly active children
#     """

#     # get the % of active adults for the gender and geography specified
#     activity_df = read_activity_levels(age_group='adult', gender=gender, geography=geography, source = activity_source, local = local)

#     # get the % of active children for the gender and geography specified
#     youth_activity_df = read_activity_levels(age_group='age 5-18', gender=gender, geography=geography, source = activity_source, local = local)

#     # get the relative likelihood of being active as an adult given activity as a child
#     activity_relative_risks_df = read_relative_risks(factor='adult_activity', age_group='youth', gender=gender, geography='global', source = relative_risk_source, local = local)

#     # calculate the rate of continuing as an active adult (acitivty_persistence) and of 'converting' from being an inactive child to an active adult
#     activity_persistence, activity_converts = calculate_adjusted_risk_rates(PopulationRisk = activity_df['activity_rate'][0], 
#                                                                             PopulationActiveRate = youth_activity_df['activity_rate'][0], 
#                                                                             RelativeRisk = activity_relative_risks_df['relative_risk'][0])
    
#     # calculate the number of additionally active adults we can expect from this group
#     additional_active_adults = active_youth * (activity_persistence - activity_converts)

#     return additional_active_adults

def calculate_adjusted_risk_rates(PopulationRisk, PopulationActiveRate, RelativeRisk, PopulationFairlyActiveRate=None, FairlyActiveRelativeRisk=None):

    """
    Calculates the adjusted risk rates for active, fairly active, and inactive populations based on population risk,
    population activity rate, and relative risk.

    This uses simple algebraic manipulation to derive the required risk rates, based on the following formula:

    PopulationRisk = weighted average of active and inactive risk rates, where the weights are the share of the population that is active/inactive
                   = PopulationActiveRate * ActiveRisk + (1 - PopulationActiveRisk) * Inactive Risk
    
    When the population is segmented into three activity levels instead of two (i.e. a 'fairly active' population is defined), the weighted average on the RHS includes the fairly active rate and risk too.

    The relative risks are the ratio between the active/fairly active risk and the inactive risk.

    Args:
        PopulationRisk (float): The risk rate in the general population.
        PopulationActiveRate (float): The proportion of truly active people in the population (0 to 1).
        RelativeRisk (float): The relative risk (risk for active people / risk for inactive people).
        PopulationFairlyActiveRate (float, optional): The proportion of fairly active people in the population (0 to 1).
        FairlyActiveRelativeRisk (float, optional): The relative risk for fairly active people.

    Returns:
        tuple: A tuple containing the adjusted risk rates for active, fairly active, and inactive populations.
    """

    if PopulationFairlyActiveRate is None:

        #print('Population risk: ' + str(PopulationRisk))

        ActiveRisk = PopulationRisk/(RelativeRisk * (1 - PopulationActiveRate) + PopulationActiveRate)

        #print('Active risk: ' + str(ActiveRisk))

        InactiveRisk = ActiveRisk * RelativeRisk

        #print('Inactive risk: ' + str(InactiveRisk))

        return ActiveRisk, InactiveRisk
    
    else:

        #print('Population risk: ' + str(PopulationRisk))

        InactiveRisk = PopulationRisk/((1 - PopulationActiveRate - PopulationFairlyActiveRate) + (PopulationActiveRate * (1 / RelativeRisk)) + (PopulationFairlyActiveRate * (1/FairlyActiveRelativeRisk)))

        ActiveRisk = InactiveRisk / RelativeRisk

        FairlyActiveRisk = InactiveRisk / FairlyActiveRelativeRisk

        #print('Active risk: ' + str(ActiveRisk))

        #print('Fairly active risk: ' + str(FairlyActiveRisk))

        #print('Inactive risk: ' + str(InactiveRisk))

        return ActiveRisk, FairlyActiveRisk, InactiveRisk

def calculate_cases_saved(ActiveRisk, InactiveRisk, ActiveNum):

    ActiveAffected = ActiveRisk * ActiveNum

    InactiveAffected = InactiveRisk * ActiveNum

    CasesSaved = InactiveAffected - ActiveAffected

    return CasesSaved

#def make_dose_adjustment(BaseRisk, DoseAdjustment):

    #UpdatedRisk = BaseRisk * DoseAdjustment

    #return UpdatedRisk

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

def read_activity_levels(source, age_group, gender, geography, activity_level = 'active', local = False):

    if local:
        risks_df = pd.read_csv(source)

    filtered_df = risks_df[(risks_df['age_group'] == age_group) & (risks_df['gender'] == gender) & (risks_df['geography'] == geography) &
                           (risks_df['activity_level'] == activity_level)].reset_index()

    return filtered_df

def find_health_outcomes(additional_active, 
                         additional_fairly_active, 
                         youth = False,
                         health_list = ['coronary heart disease', 
                                        'anxiety',
                                        'depression',
                                        'stroke',
                                        'diabetes (type 2)',
                                        'breast cancer',
                                        'endometrial uterine cancer',
                                        'colon cancer',
                                        'alzheimer and other dementia',
                                        'osteoporosis'],
                        youth_health_list = ['anxiety', 'depression', 'obesity'],
                        gender = 'female',
                        geography = 'global'):
    
    """
    Calculates adult and youth health outcomes for a group of newly active children.

    This uses simple algebraic manipulation to derive the required risk rates, based on the following formula:

    PopulationRisk = weighted average of active and inactive risk rates, where the weights are the share of the population that is active/inactive
                   = PopulationActiveRate * ActiveRisk + (1 - PopulationActiveRisk) * Inactive Risk
    
    When the population is segmented into three activity levels instead of two (i.e. a 'fairly active' population is defined), the weighted average on the RHS includes the fairly active rate and risk too.

    The relative risks are the ratio between the active/fairly active risk and the inactive risk.

    Args:
        additional_active (int): The number of newly active people.
        additional_fairly_active (int): The number of new fairly active people.
        youth (boolean): Do the active and fairly active populations refer to youths or adults? Defaults to False.
        health_list (list): The list of health conditions you want to include in the analysis for adult health outcomes.

    Returns:
        dataframes: One dataframe of adult health outcomes and one dataframe of youth health outcomes.
    """

    # ADULT - HEALTH

    cases_saved_list = []

    if youth == True:

        pass
            
    else:

        affected_pop = additional_active
        fairly_affected_pop = additional_fairly_active

    activity_df = read_activity_levels(age_group='adult', gender=gender, geography='england', source = 'data/health_data/activity_levels.csv', local = True)

    fairly_activity_df = read_activity_levels(age_group='adult', gender=gender, geography='england', activity_level='fairly active', source = 'data/health_data/activity_levels.csv', local = True)

    for h in health_list:

        print(h)

        risks_df = read_relative_risks(factor=h, age_group='adult', gender=gender, geography='england', source = 'data/health_data/relative_risks.csv', local = True)

        fairly_risks_df = read_relative_risks(factor=h, age_group='adult', gender=gender, geography='england', activity_level='fairly active',
                                            source = 'data/health_data/relative_risks.csv', local = True)

        pop_df = read_population_risks(factor=h, age_group='adult', gender=gender, geography='global', source = 'data/health_data/population_risks.csv', local = True)

        pop_deaths_df = read_population_risks(factor=h, age_group='adult', gender=gender, geography='global', source = 'data/health_data/population_mortality_risks.csv', local = True)

        pop_dalys_df = read_population_risks(factor=h, age_group='adult', gender=gender, geography='global', source = 'data/health_data/population_dalys.csv', local = True)
        
        a,b,c = calculate_adjusted_risk_rates(pop_df['population_rate'][0]/pop_df['rate_per'][0], activity_df['activity_rate'][0], risks_df['relative_risk'][0],
                                            fairly_activity_df['activity_rate'][0], fairly_risks_df['relative_risk'][0])
        
        a_daly, b_daly, c_daly = calculate_adjusted_risk_rates(pop_dalys_df['population_rate'][0]/pop_dalys_df['rate_per'][0], activity_df['activity_rate'][0], risks_df['relative_risk'][0],
                                                    fairly_activity_df['activity_rate'][0], fairly_risks_df['relative_risk'][0])

        a_d, b_d, c_d = calculate_adjusted_risk_rates(pop_deaths_df['population_rate'][0]/pop_deaths_df['rate_per'][0], activity_df['activity_rate'][0], risks_df['relative_risk'][0],
                                                            fairly_activity_df['activity_rate'][0], fairly_risks_df['relative_risk'][0])

        cost_per_case = read_cost_per_case(factor=h, age_group='adult', gender='all', geography=geography, source = 'data/health_data/cost_per_case_adjusted.csv', local = True)

        indirect_cost_per_case = read_cost_per_case(factor=h, age_group='adult', gender='all', geography=geography, direct=False, source = 'data/health_data/cost_per_case_adjusted.csv', local = True)

        cases_saved, fairly_cases_saved = calculate_cases_saved(a, c, affected_pop), calculate_cases_saved(b, c, fairly_affected_pop)

        deaths_saved, fairly_deaths_saved = calculate_cases_saved(a_d, c_d, affected_pop), calculate_cases_saved(b_d, c_d, fairly_affected_pop)

        dalys_saved, fairly_dalys_saved = calculate_cases_saved(a_daly, c_daly, affected_pop), calculate_cases_saved(b_daly, c_daly, fairly_affected_pop)

        cases_saved_dict = {'factor': h, 
                            'risk_active': a, 
                            'risk_inactive': c, 
                            'active_cases_saved': cases_saved,
                            'active_dalys_saved': dalys_saved,
                            'active_deaths_saved': deaths_saved,
                            'direct_cost_per_case' : cost_per_case.iloc[0,11],
                            'direct_cost_saving': (fairly_cases_saved + cases_saved) * cost_per_case.iloc[0,11],
                            'indirect_cost_per_case' : indirect_cost_per_case.iloc[0,11],
                            'indirect_cost_saving' : (fairly_cases_saved + cases_saved) *  indirect_cost_per_case.iloc[0,11],
                            'total_saving' : (fairly_cases_saved + cases_saved) * (cost_per_case.iloc[0,11] + indirect_cost_per_case.iloc[0,11])
                            }

        cases_saved_list.append(cases_saved_dict)

    cases_saved_df = pd.DataFrame(cases_saved_list)

    if youth == True:

        # YOUTH - HEALTH

        youth_cases_saved_list = []

        activity_df = read_activity_levels(age_group='age 5-18', gender=gender, geography='england', source = 'data/health_data/activity_levels.csv', local = True)

        for yh in youth_health_list:

            print(yh)

            risks_df = read_relative_risks(factor=yh, age_group='youth', gender=gender, geography='england', source = 'data/health_data/relative_risks.csv', local = True)

            pop_df = read_population_risks(factor=yh, age_group='youth', gender=gender, geography='global', source = 'data/health_data/population_risks.csv', local = True)

            a,c = calculate_adjusted_risk_rates(pop_df['population_rate'][0]/pop_df['rate_per'][0], 
                                                activity_df['activity_rate'][0],
                                                risks_df['relative_risk'][0]
                                                )
            
            cost_per_case = read_cost_per_case(factor=yh, age_group='youth', gender='all', geography='America', source = 'data/health_data/cost_per_case_adjusted.csv', local = True)

            cases_saved = calculate_cases_saved(a, c, additional_active)

            youth_cases_saved_dict = {'factor': yh, 
                                'risk_active': a,
                                'risk_inactive': c, 
                                'active_cases_saved': cases_saved,
                                'direct_cost_per_case' : cost_per_case['adjusted_cost_with_healthcare_expenditure'][0],
                                'direct_cost_saving': (fairly_cases_saved + cases_saved) * cost_per_case['adjusted_cost_with_healthcare_expenditure'][0]
                                }

            youth_cases_saved_list.append(youth_cases_saved_dict)

        youth_cases_saved_df = pd.DataFrame(youth_cases_saved_list)

    else:
        youth_cases_saved_df = pd.DataFrame()

    return cases_saved_df, youth_cases_saved_df
