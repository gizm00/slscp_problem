import pytest
from slcsp_calc import calculate_slcsp

def test_zip_in_multiple_rate_areas():
    # if a zipcode spans multiple rate areas the result slcsp is blank
    df_result = calculate_slcsp(
    'testfiles/multiple_rate_areas_zips.csv',
    'testfiles/multiple_silver_plans.csv',
    'testfiles/single_slcsp.csv'
    )
    assert df_result.iloc[[0]]['rate'][0] == None
    
def test_zip_not_in_zips():
    # if a zipcode in the slcsp input is not in the zipcode file result is blank
    df_result = calculate_slcsp(
    'testfiles/missing_zip_zips.csv',
    'testfiles/multiple_silver_plans.csv',
    'testfiles/single_slcsp.csv'
    )
    assert df_result.iloc[[0]]['rate'][0] == None
    
    
def test_no_silver_plan_rate():
    # if silver plans exist but there are no rate values result slcsp is blank
    df_result = calculate_slcsp(
    'testfiles/single_rate_area_zips.csv',
    'testfiles/no_silver_plan_rate.csv',
    'testfiles/single_slcsp.csv'
    )
    
    assert df_result.iloc[[0]]['rate'][0] == None
    
def test_no_silver_plans():
    # if no silver plans are available the result slcsp is blank
    df_result = calculate_slcsp(
    'testfiles/single_rate_area_zips.csv',
    'testfiles/no_silver_plans.csv',
    'testfiles/single_slcsp.csv'
    )
    assert df_result.iloc[[0]]['rate'][0] == None
    
def test_one_rate():
    # if only 1 rate is available this will be returned as the slcsp
    df_result = calculate_slcsp(
    'testfiles/single_rate_area_zips.csv',
    'testfiles/one_silver_plan_rate.csv',
    'testfiles/single_slcsp.csv'
    )
    assert df_result.iloc[[0]]['rate'][0] == 560
    
def test_all_same_rate():
    # if all plans have the same rate then return that rate
    df_result = calculate_slcsp(
    'testfiles/single_rate_area_zips.csv',
    'testfiles/silver_plan_same_rates.csv',
    'testfiles/single_slcsp.csv'
    )
    assert df_result.iloc[[0]]['rate'][0] == 560
    
def test_slcsp_calculation():
    # provided various rates for a given silver plan return the
    # second lowest cost rate
    df_result = calculate_slcsp(
    'testfiles/single_rate_area_zips.csv',
    'testfiles/silver_plan_mulitple_rates.csv',
    'testfiles/single_slcsp.csv'
    )
    assert df_result.iloc[[0]]['rate'][0] == 520