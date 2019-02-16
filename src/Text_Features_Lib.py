"""
Text Features Mudule
"""
###########
# Imports #
###########
import pandas as pd
import numpy as np

###########
# Globals #
###########

correlation_dict = {}

# this is for disable irrelevant warnings
pd.options.mode.chained_assignment = None

#############
# Functions #
############

def Create_Unique_Mapping(df, feature_name):
    '''
    Reture unique mapping for feature_name
    '''
    return {k: v for v, k in enumerate(df[feature_name].unique())}

def add_correlation_to_dict(df, main_feature_name, new_feature_name):
    '''
	Add new_feature_name correlation to correlation_dict, under main_feature_name.
	'''
    if main_feature_name not in correlation_dict:
        correlation_dict[main_feature_name] = dict()
    correlation_dict[main_feature_name].update({new_feature_name: df[new_feature_name].corr(df['bot'])})

def Apply_Unique_Mapping(df, feature_name):
    '''
    Apply unique mapping for feature_name.
    if featur mapping size < threshold: print mapping
    return new feature name.
	'''
	# create feature name.
    new_feature_name = '{0}_unique'.format(feature_name)
	# create and apply unique mapping 
    feature_mapping = Create_Unique_Mapping(df, feature_name)
    df[new_feature_name] = df[feature_name].map(feature_mapping)
	# add new feature correlation to dict
    add_correlation_to_dict(df, feature_name, new_feature_name)
    return new_feature_name

def Replace_Missing_Values_by_Mode(df, main_feature_name, feature_name, missing_value = 0, use_bot_mode = True):
    '''
    Replace feature_name values by their mode.
	return new feature name.
    '''
    # create feature name.
    new_feature_name = '{0}_mode'.format(feature_name)
    # get mode and replace
    if use_bot_mode:
        feature_mode = df[df['bot'] == 1][feature_name].mode()
    else:
        feature_mode = df[feature_name].mode()
    feature_mode = feature_mode.unique()[0]
    df[new_feature_name] = df[feature_name].replace(missing_value,feature_mode)
    
	# add new feature correlation to dict
    add_correlation_to_dict(df, main_feature_name,new_feature_name)
    return new_feature_name

def Replace_Nan_by_Distribution(col):
    '''
	Replace missing values in col with col distribution.
	'''
	# Get col distribution
    col_distribution = col.value_counts(normalize = True, dropna=True)
    # mask of NaNs
    msk = np.isnan(col) 
    #replace nan values with sample from distribution
    col[msk] = np.random.choice(col_distribution.index, msk.sum(), p=col_distribution.values)
    
def Replace_Missing_Values_by_Distribution(df, main_feature_name, feature_name, missing_value = 0):
    '''
	Replace missing values of feature_name with feature_name distribution.
	missing_value is the value in feature_name representing nan value.
	Return new feature name. 
	'''
    # create feature name.
    new_feature_name = '{0}_dist'.format(feature_name)
    # replace the missing value in feature_name with np.nan
    df[new_feature_name] = df[feature_name].replace(missing_value,np.nan)
    # Create columns distribution
    Replace_Nan_by_Distribution(df[new_feature_name])
    # add new feature correlation to dict
    add_correlation_to_dict(df, main_feature_name,new_feature_name)

    return new_feature_name

def Binning_by_Is_Most_Common(df, feature_name, most_common_value):
    '''
	Perform binning to feature_name by most common value.
	'''
	# Create feature name
    new_feature_name = '{0}_most_common'.format(feature_name)
	# Binning by is most common
    df[new_feature_name] = df[feature_name] == most_common_value
	# add new feature correlation to dict
    add_correlation_to_dict(df, feature_name,new_feature_name)
    return new_feature_name

def Replace_Str_by_Len(df, feature_name):
    '''
	Replace feature_name values by length.
	Return new feature name. 
    '''    
    # create feature name.
    new_feature_name = '{0}_len'.format(feature_name)
    # replace with length
    df[new_feature_name] = df[feature_name].str.len()
	# add new feature correlation to dict
    add_correlation_to_dict(df, feature_name,new_feature_name)
    return new_feature_name
    
def Add_Numeric_Features_From_Str(df, feature_name, most_common_values_dict, use_bot_mode = True, replace_by_len = True, apply_mapping = True):
    ''' 
	This function takes feature_name and create all possible features from it. 
	most_common_values_dict is dictionary of most common values. 
	Return all new features names. 
	'''
    new_features_names = []
    if apply_mapping:
	     # Apply unique mapping
        feature_name_mapping = Apply_Unique_Mapping(df, feature_name)
        new_features_names.append(feature_name_mapping)
	
        # replace missing values by mode
        feature_name_mode = Replace_Missing_Values_by_Mode(df, feature_name, feature_name_mapping, use_bot_mode = use_bot_mode)
        new_features_names.append(feature_name_mode)
        
        # replace missing values by distribution
        feature_name_dist = Replace_Missing_Values_by_Distribution(df, feature_name, feature_name_mapping)
        new_features_names.append(feature_name_dist)
    
    # binning by is most common
    if feature_name in most_common_values_dict:
        feature_name_most_common = Binning_by_Is_Most_Common(df, feature_name, 
                                                     most_common_values_dict[feature_name])
        new_features_names.append(feature_name_most_common)
    
    if replace_by_len:
      # create length feature
      feature_name_len = Replace_Str_by_Len(df, feature_name)
      new_features_names.append(feature_name_len)
    
    return new_features_names 