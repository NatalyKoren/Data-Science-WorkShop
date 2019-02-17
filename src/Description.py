###########
# Imports #
###########

import pandas as pd
import numpy as np
import requests
from textblob import TextBlob, Word
import nltk
from nltk.corpus import stopwords
from sklearn.ensemble import RandomForestRegressor
import General_Lib
from sklearn.feature_extraction.text import CountVectorizer

#############
#  Globals  #
#############

#Yandex keys for translation and language detection
apis = ["trnsl.1.1.20181221T214524Z.dca39366b84ef3a3.dbc320110157a98114e356f11d89c8078ae75642",
'trnsl.1.1.20181223T091550Z.fad414f57a374543.ef18c91f748d5676217a0d388c582e42e0593ded',
'trnsl.1.1.20181225T100830Z.72906db13bc1cf7f.a29466752cb4db906d6267cf8919b2fb8df68e2b',
'trnsl.1.1.20181225T171502Z.d0e2e5e49b6327ce.a880a30d730aca7b2ae8e557bd3978d142cfde37',
'trnsl.1.1.20181229T184159Z.73e537914b9b8f45.68f3d268c8811e497477fa58cd766830295b5efa'
'trnsl.1.1.20181229T162700Z.2ec595d31e3b05a2.382e57e22cd57acf9b40965a3eeb3dd956cd4640',
'trnsl.1.1.20181229T220553Z.2b7cb2cc8fe1ec11.adfcf5971bf3711ea2106d8d7b1e0033410da07b',
'trnsl.1.1.20181230T061634Z.edae275a34543cd7.aac540e8fc8fc9c46137a99769ac4c6784892cc1',
'trnsl.1.1.20181230T061634Z.d1055fa1222215c0.7155dd016e46c9a07dee1f974b7e7f0e2d56d3de',
'trnsl.1.1.20181230T154004Z.d55d46d6d0c7835a.79f433014e4d99dab6e0ec81f11e8eb7a66b8ab8',
'trnsl.1.1.20181230T153953Z.888e2261dd675927.cae8ce9760e10014f00fa28159aff15327332a5f',
'trnsl.1.1.20181230T181439Z.03601281bf6411ed.cd0f443a861856251959403ef28ad636089f8123']

#for language detection
hint = ['ja', 'en', 'es','ru', 'sv', 'fr', 'nl','pl','pt','zh','tr','id', 'de', 'ko', 'da','ar', 'fil','el','it','gl']

#############
# Functions #
#############

def get_next_key(curr_key):
	'''
	gets next key from apis list
	Args: 
		current key
	Returns: 
		next key if successul, else -1
	'''
	curr_ind = apis.index(curr_key)
	if len(apis)>curr_ind+1:
		print("changed key")
		return apis[curr_ind+1]
	else: return -1

def translate(text,key):
	'''
	translate a description field to English.
	Args: 
		text: a string represents an account's description
		key: Yandex key for translation
	Returns: 
		new string which represents text after translation
	'''
	url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
	data = {
        'key' : key,
        'text' : text,
        'lang' : 'en'
    }
	response = requests.post(url,data=data)
	response = response.json()
	return response

def description_trans(total_data):
	'''
	translate description column to English.
	Args: 
		total_data: data frame which represents all data
	Returns: 
		new data frame which icludes translated description.
	'''
	trans_df = total_data[['id','lang','description','bot']].copy()
	trans_df['translation'] = ''
	total_data['description'].fillna('', inplace = True)
	for i in range(len(trans_df)): #go over each description and translate it
		if len(trans_df['description'][i]) > 0:
			res = translate(trans_df['description'][i], apis[0])
			while res['code']==404:
				api_key = get_next_key(api_key)
				if api_key == -1:
					print('no free keys')
					break
				res = translate(text, api_key)
			if res['code'] == 200:
				trans_df['translation'][i] = res['text']
			else:
				continue
		else:
			trans_df['translation'][i] = ''
	trans_df.to_csv('user_bot_desc_translations5.csv')
	return trans_df

def preprocess(s):
	'''
	preprocess each description field before creating a dictionary.
	includes: lower case all strings, remove punctuation and numbers, spelling correction,
	removing stopwords and lemmatization.
	Args: 
		s: a string represents an account's description
	Returns: 
		new string which represents s after preprocessing
	'''
	s=s.lower()
	tokens = nltk.word_tokenize(s)
	new_tokens = []
	stop = stopwords.words('english')
	for token in tokens:
		if token.isalpha():
				token = " ".join(token for token in token.split() if token not in stop)
				token = str(TextBlob(token).correct())
				token = " ".join([Word(word).lemmatize() for word in token.split()])
				new_tokens.append(token)
	return " ".join(new_tokens)
	
def important_words_understanding(X_train,y_train,all_data):
	'''
	using feature importance of random forest in order to understand
	what are the 10 most important words in the text.
	Args: 
		X_train: X of train data frame
		y_train: y of train data frame
		all_data: data frame of all data
	Returns: 
		10 most important words
	'''
	rfc = RandomForestRegressor(n_estimators=20, random_state=0)  
	rfc.fit(X_train, y_train)
	feature_importances = pd.DataFrame(rfc.feature_importances_,
								   index = X_train.columns,
								   columns=['importance']).sort_values('importance',ascending=False)
	return feature_importances.index.values[0:10]
	
	
def add_columns_for_division_and_merging(description_df,bow,dictionary):
	'''
	adding 'test_set_1' and 'test_set_2' in order to divide the data later, adding 'id' column in order to merge 
	to a complete df and 'bot' in order to evaluate words.
	Args: 
		description_df: description data frame
		bow
		dictionary
	Returns: 
		data frame that includes new columns
	'''
	mat_test_set_1 = description_df['test_set_1'].as_matrix()
	mat_test_set_2 = description_df['test_set_2'].as_matrix()
	mat_bot = description_df['bot'].as_matrix()
	mat_index = description_df['id'].as_matrix()
	count_vectors_df = pd.DataFrame(bow,columns = dictionary)
	count_vectors_df.insert(loc= 0, column='main_id', value=mat_index)
	count_vectors_df.insert(loc= len(bow[0]),column='test_set_1', value=mat_test_set_1)
	count_vectors_df.insert(loc= len(bow[0])+1,column='test_set_2', value=mat_test_set_2)
	count_vectors_df.insert(loc= len(bow[0])+2,column='is_bot', value=mat_bot)
	return count_vectors_df
	
	
def X_y_division(data, cols_to_remove):
	'''
	divide data by target value to X,y
	Args: 
		data: data frame to split
		cols_to_remove: columns to remove from full data frame
	Returns: 
		2 splits of data frame
	'''
	y_data = data['is_bot']
	X_data = data.drop(cols_to_remove, axis=1)
	return X_data, y_data
	
def find_important_words(X_train, y_train):
	'''
	find important words in description column.
	Args: 
		X_train
		y_train
	Returns: 
		a list of 10 most important words
	'''
	RFclassifier = RandomForestRegressor(n_estimators=20, random_state=0)  
	RFclassifier.fit(X_train, y_train)
	feature_importances = pd.DataFrame(RFclassifier.feature_importances_,
									index = X_train.columns,
									columns=['importance']).sort_values('importance',ascending=False)
	return feature_importances.index.values[0:10]

def detect(text,key):
	'''
	detect the language of a description.
	Args: 
		text: description text
		key: Yandex key
	Returns: 
		response of the translation
	''' 
	url = "https://translate.yandex.net/api/v1.5/tr.json/detect"
	data={
		'key' : api_key,
		'text':text,
		'hint':hint
	}
	response = requests.post(url,data=data)
	response = response.json()
	return response
    
def add_language_detection(description_df):
	'''
	detect the language of each description.
	Args: 
		description_df: description data frame
	Returns: 
		data frame which incudes a column of detected language
	''' 
	description_df['description_lang'] = ''
	api_key = apis[0]
	for i in range(len(description_df)):
		if description_df['description_lang'][i] == '':
			description_df['description_lang'][i] =  description_df['lang'].get(i)
			continue
		res = detect(description_df['description'].get(i), api_key)
		while res['code'] == 404:
			api_key = get_next_key(api_key)
			if api_key == -1:
				print('no free keys')
				break
			res = detect(description_df['description'].get(i), api_key)
		if res['code'] == 200:
			description_df['description_lang'][i] = res['lang']
	return description_df

def find_important_words_from_bow(description_df):
	'''
	creating a bow and finding 10 most important words
	Args: 
		description_df: description data frame
	Returns: 
		a list of ten most important words and count_vectors_df
	'''
	# # # # creating BoW # # # # #
	vectorizer = CountVectorizer(preprocessor=preprocess)
	bow = vectorizer.fit_transform(description_df['translation'].values.astype(str)).toarray()
	dictionary = vectorizer.get_feature_names()

	# # # # add columns for division and divide data # # # # #
	count_vectors_df = add_columns_for_division_and_merging(description_df,bow,dictionary)
	cv_train_data, cv_test_set_1, cv_test_set_2 = General_Lib.train_test_division(count_vectors_df)
	X_cv_train, y_cv_train = X_y_division(cv_train_data, cols_to_remove = ['main_id'])

	# # # # find and extract most important words # # # # #
	important_words = find_important_words(X_cv_train, y_cv_train)
	return count_vectors_df, important_words