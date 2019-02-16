###########
# Imports #
###########

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

###########
# Globals #
###########

class txt_format:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

#############
# Functions #
############

def Plot_Correlation_Matrix(df, features_list, plt_matshow = False):
    '''
	Plot the correlation matrix of features_list.
	Return features correlation matrix
	'''
    if plt_matshow:
        plt.matshow(df[features_list].corr())
    
    features_corr = abs(df[features_list].corr())
    sns.heatmap(features_corr, 
               xticklabels=features_corr.columns.values,
               yticklabels=features_corr.columns.values)
    return features_corr

def Binning(col, bin_num, bin_seq = None):
    '''
	Perform binning to col.
	bin_num - number of equal length bins.
	bin_seq - if bin_seq is not None, binning col by bin_seq values. 
	'''
    # define labels according to bin_num and bin_seq params.
    if bin_seq is None:
        labels = range(bin_num)
        bin_seq = bin_num
    else:
        labels = range(1,len(bin_seq))
    
    #Binning using cut function of pandas
    colBin = pd.cut(col,bin_seq,labels=labels,include_lowest=True)
    return colBin

def Print_Numeric_Features(df):
   '''
   Print all the numeric features in df.
   '''
   # Numeric types
   numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
   numeric_df = df.select_dtypes(include=numerics)
   print('{0}{1}{2}{3}{3}'.format(txt_format.BOLD,txt_format.UNDERLINE,'Numeric features:',txt_format.END))
   for feature in numeric_df.columns:
       print(feature) 
       
def Print_Target_Features_Correlation(df, corr_methods, target_feature, features_list_to_drop):
    '''
    Print top 10 correltation between df features and target feature
    Params:
        df- data frame
        corr_methods- correlation methods to use (iterable).
        target_feature - target feature name
        features_list_to_drop - features list to drop from df (no need to calculate correlation for those features)
    '''
      
    correlations_lists = []
    print('{0}{1}{2}{2}'.format(txt_format.BOLD,
          '---------------Target - Feature Correlations---------------',
          txt_format.END))
    print('')
    # For each correlation method
    for method_name in corr_methods:
        method_corr_list = []
        #Calculate correlation
        for col_name in df.drop(features_list_to_drop,axis =1).columns:
            if col_name == 'id':
                corr = df[target_feature].corr(df[col_name].astype('float64'),method=method_name)
            else:
                corr = df[target_feature].corr(df[col_name],method=method_name)
            method_corr_list.append((col_name,corr))
    
        #Print top 10 correlations
        method_corr_list.sort(key = lambda x:abs(x[1]), reverse = True)
        correlations_lists.append((method_name,method_corr_list))
    
        str_to_print = '*** {0} best 10 correlation results ***'.format(method_name)
        print('{0}{1}{2}{2}'.format(txt_format.BOLD,str_to_print,txt_format.END))
        for feature,corr in method_corr_list[0:11]:
            print(feature,corr)
        print('')
        
def Print_Best_Var(df, target_feature, features_list_to_drop):
    '''
    Print best 10 var in df
    Params:
        df - data frame
        target_feature - target feature name
        features_list_to_drop - features list to drop from df (no need to calculate variance for those features)
    '''
    
    print('{0}{1}{2}{2}'.format(txt_format.BOLD,
          '--------------- Best 10 var results ---------------',
          txt_format.END))
    
    var_list = []
    for col_name in df.drop(features_list_to_drop,axis =1).columns:
        var_list.append((col_name,df[col_name].astype('float64').var()))
    
    var_list.sort(key = lambda x:x[1])
    

    for feature,var in var_list[0:11]:
        print(feature,var)
		
def train_test_division(df):
	'''
	divide data by 'test_set_1' and 'test_set_2' columns.
	Args: 
		df: data frame to split
	Returns: 
		3 splits of data frame
	'''
	test_set_1 = df[df['test_set_1'] == 1]
	test_set_2 = df[df['test_set_2'] == 1]
	train = df[df['test_set_1'] == 0]
	train_data = train[train['test_set_2'] == 0]
	train_data = train_data.drop(['test_set_1','test_set_2'], axis = 1)
	test_set_1 = test_set_1.drop(['test_set_1','test_set_2'], axis = 1)
	test_set_2 = test_set_2.drop(['test_set_1','test_set_2'], axis = 1)
	return train_data, test_set_1, test_set_2