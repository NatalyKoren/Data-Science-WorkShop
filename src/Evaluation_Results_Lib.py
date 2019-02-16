###########
# Imports #
###########
import sklearn.metrics
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import os, json

###########
# Globals #
###########

results_dict = dict()
#Those globals should be set by the user
base_file_path = ''
count = 0
csv_file_name = ''
json_file_name = ''
compare_file_name = ''
data_set_change = ''
base_results_file = ''

#############
# Functions #
############

def print_results(y_true, y_predicted, analyze_results = False, classifier_name = None):
    '''
	Print results evaluation.
	'''
    cm_dt = confusion_matrix(y_true, y_predicted)
    classification_report_str = classification_report(y_true, y_predicted)
    accuracy = accuracy_score(y_true, y_predicted)
    MCC = matthews_corrcoef(y_true, y_predicted)
    Specificity = cm_dt[1,1]/(cm_dt[1,0]+cm_dt[1,1])
    print("Confusion Matrix :")
    print(cm_dt)  
    print("Classification Report :")
    print(classification_report_str)
    print("Accuracy : ",accuracy)
    print("MCC : ",MCC)
    print("Specificity : ",Specificity)
    if analyze_results:
        # output_dict need sklearn version 0.20
        classification_report_dict = classification_report(y_true, y_predicted,output_dict=True)
        results_dict[classifier_name] = get_dict_results(classification_report_dict,accuracy,MCC,Specificity)
        
def get_dict_results(dict_values, accuracy, MCC, Specificity, round_digit = 2):
    '''
	Get results from dict_values.
	Return dict with relevant results. 
	'''
    base_results = dict_values['weighted avg']
    dict_res = {
        'precision': round(base_results['precision'],round_digit),
        'recall': round(base_results['recall'],round_digit),
        'f1-score': round(base_results['f1-score'],round_digit),
        'accuracy': round(accuracy,round_digit),
        'MCC': round(MCC,round_digit),
        'Specificity': round(Specificity,round_digit)
    }
    return dict_res

def write_dict_results_to_csv(results_file_path, results_dict):
    '''
    Write results_dict to results_file_path. 
	'''
    with open(results_file_path, 'w') as file:
        file.write(data_set_change)
        file.write(os.linesep)
        for (classifier,classifier_res) in results_dict.items():
            header = [classifier, 'score', 'base_score', 'delta (current - base)','percentage', 'improvement (current/base)']
            file.write(','.join(header))
            file.write('\n')
            for (property_name,score) in classifier_res.items():
                if(type(score) is tuple or type(score) is list):
                    score_str = ','.join(str(arg) for arg in score)
                else:
                    score_str = str(score)
                file.write('{0},{1}\n'.format(property_name,score_str))
                file.write(os.linesep)
                
    file.close()
    
def get_improvement_results(results_dict):
    '''
	Get improvement results of results_dict comparing to compare_file_name results. 
	results_dict contains results for each classifier.
	results of each classifier contains: precision, recall, f1-score, accuracy, MCC, specificity.
	Calculate improvement for each classifier.
	Fields calculated:
	improvement = current result - base result
	percentage = percentage of improvement
	mult = current result / base result
	return dict of improvement results for each classifier. 
	'''
	# make copy of results_dict
    results_dict_imprv = dict(results_dict)
    # load base results
    base_results_file_path = os.path.join(base_file_path, 'results', compare_file_name)
    with open(base_results_file_path) as file:
        base_results_dict = json.load(file)
    file.close()
	# calculate improvement for each classifier
    for (classifier,classifier_res) in results_dict.items():
        base_classifier_results = base_results_dict[classifier]
        for (property_name,score) in classifier_res.items():
            base_score = base_classifier_results[property_name]
            if(type(base_score) is tuple or type(base_score) is list):
                base_score = float(base_score[0])
            else:
                base_score = float(base_score)
            improvement = round(score - base_score,2)
            if  base_score == 0.:
                base_score = 1
            percentage = round((improvement/base_score)*100.0,2)
            mult = round(score/base_score,2)
            results_dict_imprv[classifier][property_name] = (score,base_score,improvement,percentage,mult)
    return results_dict_imprv

def Analyze_Results(results_analyzer = False, compare_results = False):
    '''
	Analyze results of all the classifiers.
	compare_results - compare the current results to previous results.
    Write the results to csv and json file. 	
	'''
    if not results_analyzer:
        return
    
    # dump to  json file
    if compare_results:
        results_dict = get_improvement_results(results_dict)
    json_results_file_path = os.path.join(base_file_path, 'results', json_file_name)
    with open(json_results_file_path, 'w') as file:
        json.dump(results_dict,file, indent=2)
    # write to csv file
    results_file_path = os.path.join(base_file_path, 'results', csv_file_name)
    write_dict_results_to_csv(results_file_path, results_dict)
    return

#############
# ROC- AUC #
############
def Plot_Roc(fpr, tpr, auc,classifier):
    '''
	Plot ROC curve.
	'''
    plt.figure()
    plt.plot(fpr, tpr, label='ROC curve (AUC = %0.2f)' % auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic {0}'.format(classifier))
    plt.legend(loc="lower right")
    plt.show()
    
def Plot_PR(precision, recall):
    '''
	Plot precision-recall curve.
	'''
    plt.figure()
    plt.plot(recall, precision, label='PR curve')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision Recall curve')
    plt.legend(loc='lower left')
    plt.show()
 
def Plot_Metrics(expected,predicted,classifier):
    '''
	Plot ROC and precision-recall curve, of expected and predicted results. 
	'''
    y_true = expected
    y_score = predicted
    auc = sklearn.metrics.roc_auc_score(y_true, y_score)
    fpr, tpr, thresholds = sklearn.metrics.roc_curve(y_true, y_score)
    Plot_Roc(fpr, tpr, auc, classifier)
    precision, recall, thresholds = sklearn.metrics.precision_recall_curve(y_true, y_score, pos_label=1)
    Plot_PR(precision, recall)
    