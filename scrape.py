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
			final_data.append(1)
		else:
			final_data.append(0)
	
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

	for filename in filenames:
		with open(os.path.join(os.getcwd(), os.path.join(dir_name,filename))) as data_file:
			data = json.load(data_file)
		
		description_lengths.extend(getDescriptionLength(data))
		
		mttr.extend(getOpeningClosingTime(data))

	mttr = [ diffInDays(x, y) for x, y in mttr ]
	
	zipped = zip(mttr, description_lengths)
	zipped = [(x, y) for x, y in zipped if x != -1 and y != 0]
	
	#zipped = normalize(np.array(zipped), axis = 0, norm = 'max')
	
	#pprint(np.array(zipped))
	
	mttr, description_lengths = map(list, zip(*zipped))
	#mttr = normalize(np.array(mttr), norm = 'max')
	#description_lengths = normalize(np.array(description_lengths), norm = 'max')
	
	print len(mttr)
	
	plt.scatter(mttr, description_lengths)
	plt.grid()
	
	#plt.show()
	
	print scipy.stats.spearmanr(mttr, description_lengths)
	print scipy.stats.pearsonr(mttr, description_lengths)
	
	
	
	
	
	
	
		
