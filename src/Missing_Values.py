###########
# Imports #
###########
import numpy as np

#############
# Functions #
############

# Ratio of nan values on genuine user accounts or bot accounts
def Print_Nan_Ratio(total_data,col_name, is_bot_account):
    global txt_format
    global bot_count
    global genuine_users_count
    nan_count = np.sum(total_data[total_data['bot'] == is_bot_account][col_name].isnull())
    if is_bot_account:
        total_count = bot_count
        account_type = 'bot'
    else:
        total_count = genuine_users_count
        account_type = 'genuine users'
    ratio = nan_count*1.0/total_count
    print('{0}{1}{2}{3}{3}'.format(txt_format.BOLD,txt_format.UNDERLINE,col_name,txt_format.END))
    print('ratio of nan values on {0} account: {1}'.format(account_type,ratio))