#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 10:06:06 2019

@author: michalwasserlauf
"""
import os
import pandas as pd
import numpy as np

Date_Format = '%a %b %d %H:%M:%S +0000 %Y'

def calc_avg_tweets_per_hour(tweet_df):
    """
    input : dataframe with all tweets of a certain user
    returns: the average number of tweets per hour this user posts
    """
    count_df = tweet_df.groupby([pd.Grouper(key='timestamp',freq='H')]).size().reset_index(name='count')
    count_df = count_df[count_df['count']>0]
    avg = count_df['count'].mean()
    return avg

def calc_prop_tweet_features(tweet_data):
    """
    input: dataframe with whole tweet data
    return: datafame containing the numerical tweet-based features for each user having tweets
    """
    user_data = pd.DataFrame()
    user_data['id'] = tweet_data['user_id'].unique()
    user_data['p_retweet']=0
    user_data['p_favorites']=0
    user_data['p_hashtags']=0
    user_data['p_urls']=0
    user_data['p_mentions']=0
    user_data['avg_tweets_per_hour']=0.0
    user_data = pd.merge(user_data,tweet_data[['user_id','bot']], how = 'inner', left_on = 'id', right_on = 'user_id',
                               left_index = True)
    user_data = user_data.drop_duplicates()
    
    for uid in user_data['id']:
        u_tweets = tweet_data[tweet_data['user_id']==uid]
        n_tweets = len(u_tweets)
        retweet_sum = u_tweets['retweet_count'].sum(axis=0)
        fav_sum = u_tweets['favorite_count'].sum(axis=0)
        hash_sum = u_tweets['num_hashtags'].sum(axis=0)
        mention_sum = u_tweets['num_mentions'].sum(axis=0)
        urls_sum = u_tweets['num_urls'].sum(axis=0)
        ind = user_data.index[user_data['id'] == uid]
        
        user_data['avg_tweets_per_hour'][ind] = calc_avg_tweets_per_hour(u_tweets)
        user_data['p_retweet'][ind] = retweet_sum
        if retweet_sum > 0:
            user_data['p_retweet'][ind] /= n_tweets
           
        user_data['p_favorites'][ind] = fav_sum
        if fav_sum > 0:
            user_data['p_favorites'][ind] /= n_tweets
           
        user_data['p_hashtags'][ind] = hash_sum
        if hash_sum > 0:
            user_data['p_hashtags'][ind] /= n_tweets
           
        user_data['p_urls'][ind] = urls_sum
        if urls_sum > 0:
            user_data['p_urls'][ind] /= n_tweets
           
        user_data['p_mentions'][ind] = mention_sum
        if mention_sum > 0:
            user_data['p_mentions'][ind] /= n_tweets

    return user_data

def preprocess(text):
    """
    cleaning the tweets before calculating Levenshtein distance
    input : tweet (text)
    returns: cleaned tweet: 1. replacing each url with the string --LINK--
                            2. replacing each mention with the string --MENTION--
                            3. collecting all #HASHTAGS, sorting them and pushing them to the end of the tweet
    """
    toks = text.split(' ')
    toks = list(filter(None,toks))
    hashtags = []
    for t in toks: #to avoid index errors
        if '#' in t:
            hashtags.append(t)
            toks.remove(t)
    for i in range(len(toks)):
        if 'https://' in toks[i]:
            toks[i] = toks[i][:toks[i].rindex('https://')] + '--LINK--'
        if '@' in toks[i]:
            toks[i] = toks[i][:toks[i].rindex('@')] + '--MENTION--'
    hashtags = sorted(hashtags)
    toks.extend(hashtags)
    return ' '.join(toks)

def levenshtein(s1, s2):
    """
    calculate Levenshtein distance between two tweets
    input: two tweets(text) s1 and s2
    output: Levenshtein distance between these
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def tweet_dist_var(tweets_lst):
    """
    wrapper function. 
    Calculating the levenstein distances between every two tweets
    and returning the variance of these distances
    """
    dist = []
    for i in range(len(tweets_lst)):
        for j in range(i+1,len(tweets_lst)):
            text1 = preprocess(tweets_lst[i])
            text2 = preprocess(tweets_lst[j])
            res = levenshtein(text1,text2)
            dist.append(res)
    if np.sum(dist)==0 or len(dist)==0:
        return 0.0
    return np.var(dist)

def calc_tweet_var_for_user(tweets,sample,sample_ids,fname,is_human):
    for i,uid in enumerate(sample_ids):
        u_tweets = tweets[tweets['user_id']==uid]
        if u_tweets.shape[0]==1:
            continue
        if is_human:
            rand_tweets = u_tweets.sample(frac=0.1)
        elif u_tweets.shape[0]>300:
            rand_tweets = u_tweets.sample(n=300)
        else:
            rand_tweets = u_tweets
        ind = sample.index[sample['id'] == uid].tolist()[0]
        sample['tweet_var'][ind] = tweet_dist_var(rand_tweets['text'].tolist())
        if i%20==0:
            print('Processed tweet_var for {} users out of {}'.format(i+1,sample.shape[0]))
            sample.to_csv(fname+'_sample_lev.csv')
        if i+1==sample.shape[0]:
            print('done processing tweet_var for sample of ' + fname)
            sample.to_csv(fname+'_sample_lev.csv')
    return sample

def calc_bot_tweet_var(file_list): #return a dict containig file name as key and 
    print('calculating for bots')
    df_d={}
    for file in file_list:
        print('loaded '+file)
        tweets = pd.read_csv(file,usecols=['id','text','user_id'],dtype=str)
        tweets.dropna(subset=['text'],inplace=True) #remove tweets with no text
        users = pd.DataFrame()
        users['id'] = tweets['user_id'].unique()
        sample = users.sample(n=200)
        sample['tweet_var'] = 0.0
        print(str(sample.shape[0])+' users to process')
        sample_ids = sample['id'].tolist()
        fname = file.replace('_tweets.csv','') #for debugging add _try
        df_d[fname]= calc_tweet_var_for_user(tweets,sample,sample_ids,fname,is_human=0)
    return df_d

def calc_human_tweet_var(file_list):
    print('calculating for humans')
    tweets = pd.DataFrame()
    for file in file_list:
        print('loaded '+file)
        temp = pd.read_csv(file,usecols=['id','text','user_id'],dtype=str)
        tweets = pd.concat([tweets,temp], ignore_index = True)
    tweets.dropna(subset=['text'],inplace=True) #remove tweets with no text
    users = pd.DataFrame()
    users['id'] = tweets['user_id'].unique()
    sample = users.sample(n=1000)
    sample['tweet_var'] = 0.0
    print(str(sample.shape[0])+' users to process')
    sample_ids = sample['id'].tolist()
    fname = 'human'
    return calc_tweet_var_for_user(tweets,sample,sample_ids,fname,is_human=1)

def get_tweets_files_names(dataset_dir, tweets_dir, genuine_tweets_dir, bot_tweets_dir):
    """
    Get all tweets file names splitted to genuine users file names and bot file names.
    """
    tweets_directory = os.path.join(os.getcwd(), dataset_dir, tweets_dir)
    genuine_tweets_dir = os.path.join(tweets_directory, genuine_tweets_dir)
    bot_tweets_dir = os.path.join(tweets_directory, bot_tweets_dir)
    genuine_tweets_files_names = [file 
                                  for file in os.listdir(genuine_tweets_dir) 
                                  if os.path.isfile(os.path.join(genuine_tweets_dir, file))
                                 ]
    
    bot_tweets_files_names = [file 
                              for file in os.listdir(bot_tweets_dir) 
                              if os.path.isfile(os.path.join(bot_tweets_dir, file))
                             ]
    
    return genuine_tweets_files_names,bot_tweets_files_names


def run_tweet_var_calculation():
    """
    wrapping the whole process of calculating the tweet_var feature, including fillng the missing value
    by mean: if human user- fill in with the mean value of tweet_var for humans.
             if bot - fill in with the mean value of tweet_var for of the matching bot type.
    returns: dataframe containing id of users ans their tweet_var and range feature.
    """
    print('Calculating tweet_var')
    prev_dir = os.getcwd()
    File_Path = os.path.join(prev_dir, 'Datasets', 'Tweets')
    os.chdir(File_Path)

    human_tweets_lst = ['E13_tweets.csv','genuine_accounts_tweets.csv','TFP_tweets.csv']
    bot_tweets_lst = ['fake_followers_tweets.csv','social_spambots_1_tweets.csv','social_spambots_2_tweets.csv',
       'social_spambots_3_tweets.csv','traditional_spambots_1_tweets.csv']
    
    
    bot_tweet_var_dict = calc_bot_tweet_var(bot_tweets_lst)
    human_tweet_var_df = calc_human_tweet_var(human_tweets_lst)
    
    human_users_lst = ['E13_users.csv','genuine_accounts_users.csv','TFP_users.csv']
    bot_users_lst = ['fake_followers_users.csv','social_spambots_1_users.csv','social_spambots_2_users.csv',
       'social_spambots_3_users.csv','traditional_spambots_1_users.csv','traditional_spambots_2_users.csv',
       'traditional_spambots_3_users.csv','traditional_spambots_4_users.csv']
    
    total_users_human = pd.DataFrame()
    for file in human_users_lst:
        tmp_df = pd.read_csv(file,usecols=['id'],dtype=str)
        total_users_human = pd.concat([total_users_human,tmp_df],ignore_index=True)
    total_users_human['bot'] = 0
    
    mean_vals = {}
    for fname in bot_tweet_var_dict:
        df = bot_tweet_var_dict[fname]
        mean_vals[fname] = df['tweet_var'].mean()
        
    total_users_bots = pd.DataFrame()
    for file in bot_users_lst:
        fname = file.replace('_users.csv','')
        tmp_df = pd.read_csv(file,usecols=['id'],dtype=str)
        if fname not in ['traditional_spambots_2','traditional_spambots_3','traditional_spambots_4']:
            tmp_df = pd.merge(tmp_df,bot_tweet_var_dict[fname],how='outer')
            tmp_df['tweet_var'].fillna(mean_vals[fname],inplace=True)
        else:
            tmp_df['tweet_var']=mean_vals['traditional_spambots_1']
        total_users_bots = pd.concat([total_users_bots,tmp_df],ignore_index=True)
    total_users_bots['bot'] = 1
    
    human_mean_val = human_tweet_var_df['tweet_var'].mean()
    total_users_human = pd.merge(total_users_human,human_tweet_var_df, how='outer')
    total_users_human.fillna(human_mean_val,axis=1,inplace=True)
    
    
    total_users = pd.concat([total_users_human,total_users_bots], ignore_index = True)
    total_users['500<var<750'] = 2
    for i in range(total_users.shape[0]):
        total_users['500<var<750'][i] = 1 if 500 < total_users['tweet_var'][i] < 750 else 0
    ##also calculate here the other tweet features
    total_users.to_csv('tweet_var+range_example.csv')
    message="""tweet_var_example.csv is in "sample_lev" directory.\n
    The sample is calculated on a really small example, since tweet_var calculation is might takes a long time.\n
    The tweet_var of users not in sample is filled with mean."""
    print(message)        
    os.chdir(prev_dir)
    return total_users

def generate_full_tweets_file(files_list):
    """
    Generate and return one csv file from files_list files. 
    """
    total_df = pd.DataFrame()

    for file in files_list:
        df = pd.read_csv(file)        
        total_df = pd.concat([total_df,df], ignore_index = True)

    total_df.drop('Unnamed: 0', axis=1, inplace=True)
    return total_df

def get_full_files_path(file_name_pattern, files_list, beginning_path):
    """
    Return a list of full path file names, 
    only for files in files_list containing file_name_pattern. 
    """
    
    return [os.path.join(beginning_path,file)
            for file in files_list
            if file_name_pattern in file]  
    
def generate_all_tweets_files(tweets_file_names_lst, tweets_split_files_names_lst, 
                              beginning_path, tweets_dir):
    
    """
    Reconstruct each csv file in tweets_file_names_lst.
    The csv file split names is found in tweets_split_files_names_lst.
    Write the new united file to csv file inside tweets directory. 
    """
       
    for file in tweets_file_names_lst:
        files_list = get_full_files_path(file[:-4], tweets_split_files_names_lst, beginning_path)
        
        full_df = generate_full_tweets_file(files_list)
        out_name = os.path.join(tweets_dir, file)
        full_df.to_csv(out_name)
        

def generate_all_tweets_datasets(dataset_dir, tweets_dir, genuine_tweets_dir, bot_tweets_dir):
    """
    Reconstruct all tweets split files. 
    Each split file will be written to one csv file. 
    """
    
    human_tweets_lst = ['E13_tweets.csv',
                        'genuine_accounts_tweets.csv',
                        'TFP_tweets.csv']
    bot_tweets_lst = ['fake_followers_tweets.csv',
                      'social_spambots_1_tweets.csv',
                      'social_spambots_2_tweets.csv',
                      'social_spambots_3_tweets.csv',
                      'traditional_spambots_1_tweets.csv']
    
    genuine_tweets_files,bot_tweets_files = get_tweets_files_names(dataset_dir, 
                                                                   tweets_dir, 
                                                                   genuine_tweets_dir, 
                                                                   bot_tweets_dir
                                                                   )
    
    tweets_dir =  os.path.join(os.getcwd(), dataset_dir, tweets_dir)
    generate_all_tweets_files(human_tweets_lst, genuine_tweets_files, 
                               os.path.join(tweets_dir, genuine_tweets_dir), tweets_dir)
    
    generate_all_tweets_files(bot_tweets_lst, bot_tweets_files, 
                               os.path.join(tweets_dir, bot_tweets_dir), tweets_dir)        