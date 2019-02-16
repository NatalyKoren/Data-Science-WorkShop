###########
# Imports #
###########

import pandas as pd
from textblob import TextBlob, Word
import nltk
from nltk.corpus import stopwords
from sklearn.ensemble import RandomForestRegressor
from yandex.Translater import Translater
import General_Lib
from sklearn.feature_extraction.text import CountVectorizer

#############
# Functions #
############

def translate(text,key):
	'''
	translate each description field to English.
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
	try:
		response = requests.post(url,data=data)
	except:
		print('yandex error')
		return {'code':0,'text':text}
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
	api_key1 = 'trnsl.1.1.20181229T184159Z.73e537914b9b8f45.68f3d268c8811e497477fa58cd766830295b5efa'
	api_key2 = 'trnsl.1.1.20190103T080420Z.4ad459876bd69d62.be2c000d6183ba3815df6f135731377444176612'
	trans_df = total_data[['id','lang','description','bot']].copy()
	for i in range(len(trans_df)): #go over each description and translate it
		#if trans_df['lang'][i] not in ['en','en-gb','en-GB','en-AU'] and 
		if len(trans_df['description'][i]) > 0:
			if i < 8000:
				res = translate(trans_df['description'][i], api_key1)
			else:
				res = translate(trans_df['description'][i], api_key2)
			if res['code'] == 200:
				trans_df['translation'][i] = res['text']
				n_chars += len(trans_df['description'][i])
			elif res['code']==404:
				print(i)
				break
			else:
				print(res)
				print(i)
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
	
def add_language_detection(description_df):
	'''
	detect the language of each description.
	Args: 
		description_df: description data frame
	Returns: 
		data frame which incudes a column of detected language
	'''
	tr = Translater()
	tr.set_key('trnsl.1.1.20190103T074752Z.686ab94789bf0b7f.9742fafedd1a8e0c37fb37161b63560cef0bf71e')
	description_df['description_lang'] = ''
	for i in range(len(description_df['description'])):
		if(i==8000):
			tr.set_key('trnsl.1.1.20190103T080523Z.77e2122f33d25363.fa90023f8951b001cbac698cccaf809da6c6a85a')
		if(description_df['description'].get(i) == ''):
			description_df['description_lang'][i] = description_df['lang'].get(i)
			continue;
		try:
			tr.set_text(description_df['description'].get(i))
			lang = tr.detect_lang()
			description_df['description_lang'][i] = lang
		except:
			print(i)
			description_df['description_lang'][i] = description_df['lang'].get(i)
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