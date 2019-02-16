###########
# Imports #
###########

import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import General_Lib

###########
# Globals #
###########

# this is for disable irrelevant warnings
pd.options.mode.chained_assignment = None


#############
# Functions #
############

def Check_For_Date_Format(df, feature_name):
    '''
    Check for date format: 
    regular date format - contains date and hour
    seconds from epoch format - number of seconds from epoch.
    return two data frames: 
        1. seconds from epoch format rows on df
        2. regular date format rows from df
    '''
    # all regular dates contain the string '+0000'
    mask = df[feature_name].str.contains('+0000', regex = False)
    seconds_from_epoch_data = df[~mask]
    regular_date_format_data = df[mask]

    # is all time stamp that does not contains +0000 are seconds from epoch format?
    seconds_from_epoch_format = seconds_from_epoch_data[feature_name].str.contains('\dL', regex = True)
    print('is all time stamp that does not contains +0000 are seconds from epoch format? {0}'
     .format(np.sum(seconds_from_epoch_format) == np.sum(~mask)))

    seconds_from_epoch_data_len = len(seconds_from_epoch_data)
    regular_date_format_data_len = len(regular_date_format_data)
    is_all_data_set_cover = seconds_from_epoch_data_len + regular_date_format_data_len == len(mask)
    print('Number of rows formatted as seconds from epoch: {0}'.format(seconds_from_epoch_data_len))
    print('Number of rows formatted as regular date: {0}'.format(regular_date_format_data_len))
    print('is seconds from epoch + regular data = all data? {0}'.format(is_all_data_set_cover))
    return seconds_from_epoch_data,regular_date_format_data

def convert_seconds_from_epoch_to_date_format(str_seconds, date_format):
    '''
    convert seconds from epoch format to date_format
    '''
    # Remove the L at the end of the string and convert to int
    seconds_int = int(str_seconds[:-1])
    # Adaptions
    seconds_int = seconds_int/1000
    return datetime.datetime.utcfromtimestamp(seconds_int).strftime(date_format)

def Rows_Contain_Seconds_From_Epoch_Format(df,feature_name):
    '''
    Return number of rows contains seconds from epoch format
    '''
    return np.sum(df[feature_name].str.contains('\dL', regex = True))

def Parse_Date_Col(df, feature_name, date_format):
    '''
    Parse date feature with date_format to int features.
    Return new features names.
    '''
    time_object = pd.to_datetime(df[feature_name], format = date_format, utc = True)
    
    # Create new features names
    day_of_the_week_feature_name = '{0}_day_of_the_week'.format(feature_name)
    month_feature_name = '{0}_month'.format(feature_name)
    day_in_month_feature_name = '{0}_day_in_month'.format(feature_name)
    hour_feature_name = '{0}_hour'.format(feature_name)
    minute_feature_name = '{0}_minute'.format(feature_name)
    second_feature_name = '{0}_second'.format(feature_name)
    year_feature_name = '{0}_year'.format(feature_name)
    
    #Create new features as int type
    df[day_of_the_week_feature_name] = time_object.dt.dayofweek
    df[month_feature_name] = time_object.dt.month
    df[day_in_month_feature_name] = time_object.dt.day
    df[hour_feature_name] = time_object.dt.hour
    df[minute_feature_name] = time_object.dt.minute
    df[second_feature_name] = time_object.dt.second
    df[year_feature_name] = time_object.dt.year
    
    return [
            day_of_the_week_feature_name,  
            month_feature_name,
            day_in_month_feature_name ,
            hour_feature_name,
            minute_feature_name,
            second_feature_name,
            year_feature_name
           ]
    
def Parse_Feature_and_Print_Corr(df, feature_name, target_feature_name, date_format):
    '''
    Parse date feature with date_format to int features. 
    Print correlation matrix with target feature.
    Return new features names and correlation matrix.
    '''
    # Parse to int features.
    new_features_names = Parse_Date_Col(df, feature_name, date_format)
    # Print correlation matrix with target feature.
    new_features_names.append(target_feature_name)
	# Plot correlation matrix
    features_corr = General_Lib.Plot_Correlation_Matrix(df, new_features_names)
    return new_features_names,features_corr
