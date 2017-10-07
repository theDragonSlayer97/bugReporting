import json
from pprint import pprint
import os

import numpy as np
import scipy.stats
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt


from datetime import datetime
date_format = "%Y-%m-%d"

dir_names = [name for name in os.listdir(os.getcwd()) if os.path.isdir(name)]

#Removing the temporary .git directory
dir_names = [name for name in dir_names if name != '.git' and name != 'IssueNumbers']

def getOpeningClosingTime(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if 'pull' in obj['html_url']:
			continue
		#pprint(obj['labels'])
		#print any(['bug' in o['name'] for o in obj['labels']])
#		if not any(['bug' in o['name'] for o in obj['labels']]):
#			continue	
		if obj['state'] == "open":
			final_data.append((-1, -1))
		else:
			final_data.append((obj['created_at'], obj['closed_at']))
	
	return final_data
			
def getDescriptionLength(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if 'pull' in obj['html_url']:
			continue
#		if not any(['bug' in o['name'] for o in obj['labels']]):
#			continue	
		if obj['body'] == None:
			final_data.append(0)
		else:
			final_data.append(len(obj['body']))
	
	return final_data	

#Has reproduction steps or not is not very concrete searches or reproduce or reproduction step
def hasReproductionSteps(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if	'pull' in obj['html_url']:
			continue
#		if not any(['bug' in o['name'] for o in obj['labels']]):
#			continue	
		if	('Reproduce' in obj['body']) or ('reproduce' in obj['body']) or('Reproduction' in obj['body']):
			final_data.append(1)
		else:
			final_data.append(0)
	
	return final_data	

def hasLabel(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if	'pull' in obj['html_url']:
			continue
		if	len(obj['labels']) > 0:
			final_data.append(True)
		else:
			final_data.append(False)
	
	return final_data	
	
def setOfDistinctLabels(json_data, label_set):
	
	for obj in json_data['data']:
		if 'pull' in obj['html_url']:
			continue
		for label in obj['labels']:
			if label['name'] not in label_set:
				label_set[label['name']] = 1
			else:
				label_set[label['name']] += 1
		
	return label_set
	
def getIssueNumbers(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if 'pull' in obj['html_url']:
			continue
		final_data.append(obj['number'])
	
	return final_data
	
def diffInDays(first, second):
	if first == -1:
		return -1
	first = datetime.strptime(first[0:10], date_format)
	second = datetime.strptime(second[0:10], date_format)
	
	return (second - first).days
	

	
for dir_name in dir_names:
	print 'For ', dir_name, ' : -'
	filenames = os.listdir(os.path.join(os.getcwd(), dir_name))

	description_lengths = list()
	mttr = list()	
	hrs = list()	

	for filename in filenames:
		with open(os.path.join(os.getcwd(), os.path.join(dir_name,filename))) as data_file:
			data = json.load(data_file)
		
		description_lengths.extend(getDescriptionLength(data))
		
		mttr.extend(getOpeningClosingTime(data))
		
		hrs.extend(hasReproductionSteps(data))

	if len(mttr) == 0 or len(description_lengths) == 0 or not any(hrs):
		continue

	mttr = [ diffInDays(x, y) for x, y in mttr ]
	
	mttr = map(float, mttr)
	description_lengths = map(float, description_lengths)
	'''
	m = max(mttr)
	
	mttr = [ val/m for val in mttr ]
	
	m = max(description_lengths)
	
	description_lengths = [ val/(1*m) for val in description_lengths]
	
	p = zip(description_lengths, hrs, mttr)
	
	temp = list()
	
	for x, y, z in p:
		if y:
			temp.append((x+0.00,z))
		else:
			temp.append((x,z))
	
	description_lengths, mttr = zip(*temp)
	'''
	#Removing Outliers
	mttr=[i for i in mttr if (abs(i - np.mean(i)) < 10 * np.std(i))]
	description_lengths=[i for i in description_lengths if (abs(i - np.mean(i)) < 2 * np.std(i))]
	print len(mttr)
	
	#plt.plot( mttr,description_lengths, 'ro')
	
	print scipy.stats.spearmanr(mttr, description_lengths)
	print scipy.stats.pearsonr(mttr, description_lengths)
	print scipy.stats.kurtosis(mttr,bias=True)
	print scipy.stats.skew(mttr,bias=True)
	plt.hist(mttr,bins=50)	
	plt.show()
	
	
	
	
		
