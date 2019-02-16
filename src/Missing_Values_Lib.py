###########
# Imports #
###########
import numpy as np
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


def Print_Nan_Ratio(df, col_name, is_bot_account):
    ''' 
    Compare nan values ratio on bot acounts or genuine user account.
	Helps to understand the missing values proportion between bot and genuine accounts. 
	'''	
	# get total genuine acounts. 
    genuine_users_count = np.sum(df['bot']==0)
    # get total bot accounts. 
    bot_count = np.sum(df['bot']==1)
    # get total missing values on col_name. 
    nan_count = np.sum(df[df['bot'] == is_bot_account][col_name].isnull())
	
    if is_bot_account:
        total_count = bot_count
        account_type = 'bot'
    else:
        total_count = genuine_users_count
        account_type = 'genuine users'
		
	# calculate ratio	
    ratio = nan_count*1.0/total_count
	# print results
    print('{0}{1}{2}{3}{3}'.format(txt_format.BOLD,txt_format.UNDERLINE,col_name,txt_format.END))
    print('ratio of nan values on {0} account: {1}'.format(account_type,ratio))
    
def Print_Missing_Values(df, size = (12,18)):
    ''' 
	Plot a chart of total missing values in df.
	'''
	# Get df missing values
    missing_df = df.isnull().sum(axis=0).reset_index()
    missing_df.columns = ['column_name', 'missing_count']
    missing_df = missing_df.loc[missing_df['missing_count']>0]
    missing_df = missing_df.sort_values(by='missing_count')

	#Plot chart
    ind = np.arange(missing_df.shape[0])
    width = 0.6
    fig, ax = plt.subplots(figsize=(12,18))
    rects = ax.barh(ind, missing_df.missing_count.values, color='blue')
    ax.set_yticks(ind)
    ax.set_yticklabels(missing_df.column_name.values, rotation='horizontal')
    ax.set_xlabel("Count of missing values")
    ax.set_title("Number of missing values in each column")
    plt.show()
    
def Fill_Missing(df):
    ''' 
	Fill all the missing values of df.
	For int and float replace with zero.
	For string, replace with empty string. 
	For utc_offset feature, replace with -1, as zero is a valid value on this feature. 	
	'''
    for col in df:
        #get dtype for column
        dtype = df[col].dtype 
        #check if it is utc offset
        if col == 'utc_offset':
            df[col].fillna(-1, inplace = True)
        #check if it is a number
        elif dtype == int or dtype == float:
            df[col].fillna(0, inplace = True)
        #object type
        else:
            df[col].fillna('' , inplace = True)