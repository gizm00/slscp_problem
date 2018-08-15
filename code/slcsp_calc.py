import pandas as pd
    
class SlcspCalc:
    """
    Generate the second lowest cost rate of a given set of silver health plans
    for a set of zipcodes
    """
    
    def __init__(self, zipfile, planfile, slcspfile):
        """
        :param zipfile: string path to file containing zipcode information, 
        see datafiles/zips.csv for expected format
        :param planfile: string path to file containing health plan information, 
        see datafiles/plans.csv for expected format
        :param slcspfile: string path to file containing zipcodes to calculate 
        second lowest cost rate silver plan (slcsp) for. See datafiles/slcsp.csv for expected format
        """
        self.__df_zips = pd.read_csv(zipfile)
        self.__df_slcsp = pd.read_csv(slcspfile)
        self.__df_plans = pd.read_csv(planfile)
        self.__df_result = None
    
    @property
    def df_result(self):
        return self.__df_result
        
    def calculate_slcsp(self):
        """
        Run the slcsp calculation using the data provided on initialization
        Results in df_result containing the list of zipcodes in df_zips and the corresponding slcsp rate
        """
        
        # filter the input data down to just the portions that are relevant given our constraints of:
        # 1. Silver health plans
        # 2. Zipcodes contained in the input slcsp file
        df_zips_sub = self.__df_zips[self.__df_zips['zipcode'].isin(self.__df_slcsp['zipcode'])]
        df_silver = self.__df_plans[self.__df_plans['metal_level'] == 'Silver']
        
        # calculate the slcsp
        df_slcp_state_ratearea = df_silver.groupby(['state','rate_area'])['rate'].apply(lambda grp: self.get_slcsp(grp)).reset_index()
        
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
        self.__df_result = self.__df_slcsp[['zipcode']].merge(droped_dupes[['zipcode','rate']], on='zipcode', how='left')
        
    def get_slcsp(self, group):
        """
        Calculate the second lowest cost rate given a group of rates
        If only 1 rate value is in the group that value will be returned
        as the second lowest cost rate
        :param group: group of numeric values
        returns numeric second lowest cost rate in the group
        """
        sorted_group = group.sort_values(ascending=True)
        min_rate = sorted_group.values[0]
        i=0
        # this initialization means that if there is only 1 rate value
        # then that will be identified as the slc rate
        slc=min_rate
        while slc == min_rate and i < len(sorted_group):
            if sorted_group.values[i] > min_rate:
                slc = sorted_group.values[i] 
            i += 1
        
        return slc
    
        
if __name__ == '__main__':
    slcsp = SlcspCalc('datafiles/zips.csv', 'datafiles/plans.csv', 'datafiles/slcsp.csv')
    slcsp.calculate_slcsp()
    slcsp.df_result.to_csv('slcsp_out.csv', index=False)
    
    
    