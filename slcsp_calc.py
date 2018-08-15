import pandas as pd
    
    
def calculate_slcsp(zipfile, planfile, slcspfile):
    """
    Given a set of inputs, caculate the second lowest cost silver health plan for a given set of zipcodes
    :param zipfile: string path to csv file containing zipcode information, 
    see datafiles/zips.csv for expected format
    :param planfile: string path to csv file containing health plan information, 
    see datafiles/plans.csv for expected format
    :param slcspfile: string path to csv file containing zipcodes to calculate 
    second lowest cost rate silver plan (slcsp) for. See datafiles/slcsp.csv for expected format
    returns: DataFrame combining the zipcodes from slcsp.csv and calculated slcsp values
    """
    df_zips = pd.read_csv(zipfile)
    df_zips = df_zips.where((pd.notnull(df_zips)), None)
    df_slcsp = pd.read_csv(slcspfile)
    df_slcsp = df_slcsp.where((pd.notnull(df_slcsp)), None)
    df_plans = pd.read_csv(planfile)
    df_plans = df_plans.where((pd.notnull(df_plans)), None)
    
    # if there are no zips or no plans return df_slcsp
    if df_zips.empty or df_plans.empty:
        return df_slcsp
    
    # filter the input data down to just the portions that are relevant given our constraints of:
    # 1. Silver health plans
    # 2. Zipcodes contained in the input slcsp file
    df_zips_sub = df_zips[df_zips['zipcode'].isin(df_slcsp['zipcode'])]
    df_silver = df_plans[df_plans['metal_level'] == 'Silver']
    
    # if there are no silver plans or no zipcodes matching the slcsp file, return df_slcsp
    if df_silver.empty or df_zips_sub.empty:
        print (df_slcsp.columns)
        return df_slcsp
    
    # calculate the slcsp
    df_slcp_state_ratearea = df_silver.groupby(['state','rate_area'])['rate'].apply(lambda grp: get_slcsp(grp)).reset_index()

    # match the slcsp back to the zipcode via state/rate_area if possible
    df_slcp_merge = df_zips_sub.merge(df_slcp_state_ratearea, on=['state','rate_area'],how='left')
    
    # disgard entries with multiple rate_areas for a given zipcode. these should be left blank
    # first, create a count of unique zipcode, area, state tuples. 
    #df_slcp_merge['count'] = df_slcp_merge.groupby(['zipcode','rate_area', 'state'])['rate'].transform('nunique')
    df_slcp_merge['count'] = df_slcp_merge.groupby(['zipcode'])['rate_area'].transform('nunique')
    
    # zero out the rate for any rows that have mulitple, unique entries
    df_slcp_merge['rate'] = df_slcp_merge.apply(lambda x: None if x['count'] > 1 else x['rate'], axis=1)
    droped_dupes = df_slcp_merge.drop_duplicates('zipcode')
    
    # join this back to the original zips file for the output
    df_result = df_slcsp[['zipcode']].merge(droped_dupes[['zipcode','rate']], on='zipcode', how='left')
    return df_result
    
def get_slcsp(group):
    """
    Calculate the second lowest cost rate given a group of rates
    If only 1 rate value is in the group or all rates are the same
    the slc will be None
    :param group: group of numeric values
    returns numeric second lowest cost rate in the group
    """
    sorted_group = group.sort_values(ascending=True)
    min_rate = sorted_group.values[0]
    slc = None
    i=0
    while slc == None and i < len(sorted_group):
        if sorted_group.values[i] is not None:
            if sorted_group.values[i] > min_rate:
                slc = sorted_group.values[i] 
        i += 1
    
    return slc
    
        
if __name__ == '__main__':
    df_result = calculate_slcsp('datafiles/zips.csv', 'datafiles/plans.csv', 'datafiles/slcsp.csv')
    df_result.to_csv('slcsp.csv', index=False)
    
    
    