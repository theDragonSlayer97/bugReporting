import json
from pprint import pprint
import os

import numpy as np
import scipy.stats
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


from datetime import datetime
date_format = "%Y-%m-%dT%H:%M:%SZ"

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
		#if not any(['bug' in o['name'] for o in obj['labels']]):
		#	continue	
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
		#if not any(['bug' in o['name'] for o in obj['labels']]):
		#	continue	
		if obj['body'] == None:
			final_data.append(0)
		else:
			final_data.append(len(obj['body'].split(' ')))
	
	return final_data	

#Has reproduction steps or not is not very concrete searches or reproduce or reproduction step
def hasReproductionSteps(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if	'pull' in obj['html_url']:
			continue
		#if not any(['bug' in o['name'] for o in obj['labels']]):
		#	continue
		if obj['body'] == None:
			final_data.append(0)
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
	
	first = datetime.strptime(first, date_format)
	second = datetime.strptime(second, date_format)
	
	days = (second-first).days
	hours = days*24 + (second-first).seconds/3600
	
	return days
	
def createRankVector(vec):
	sorted_vec = sorted(vec)
	rank = [sorted_vec.index(d) + 1 for d in vec]
	
	return rank
	
def calcPearsonRho(vec1,vec2):
	exp_x = sum(vec1)/len(vec1)
	exp_y = sum(vec2)/len(vec2)
	exp_xy = sum([x*y for x,y in zip(vec1,vec2)])/len(vec1)
	exp_x2 = sum([x**2 for x in vec1])/len(vec1)
	exp_y2 = sum([y**2 for y in vec2])/len(vec2)
	std_x = (exp_x2-(exp_x**2))**0.5
	std_y = (exp_y2-(exp_y**2))**0.5
	
	return ((exp_xy-exp_x*exp_y)/(std_x*std_y))
		
def calcSpearmanRho(vec1, vec2):

	rank1 = createRankVector(vec1)
	rank2 = createRankVector(vec2)
	
	sumDiffSq = sum([(d1-d2)**2 for d1, d2 in zip(rank1, rank2)])
	
	p = (6.0 * sumDiffSq)/(len(rank1)*(len(rank1)**2 - 1))
	
	p = 1 - p
	
	return p

def countDuplicates(vec):
	l = vec[0]
	n = list()
	freq = list()
	count = 0
	
	for i in vec:
		print i
		if i != l:
			n.append(l)
			freq.append(count)
			count += 1
			l = i
		else:
			count += 1 
	
	n.append(l)
	freq.append(count)
	
	return (n, freq)


description_lengths = list()
mttr = list()	
hrs = list()	

for dir_name in dir_names:
	print 'For ', dir_name, ' : -'
	filenames = os.listdir(os.path.join(os.getcwd(), dir_name))


	for filename in filenames:
		with open(os.path.join(os.getcwd(), os.path.join(dir_name,filename))) as data_file:
			data = json.load(data_file)
		
		description_lengths.extend(getDescriptionLength(data))
		
		mttr.extend(getOpeningClosingTime(data))
		
		hrs.extend(hasReproductionSteps(data))

		if len(mttr) == 0 or len(description_lengths) == 0 or not any(hrs):
			continue



open_date,close_date=zip(*mttr)
#For testing
open_date = open_date[0:500]
close_date = close_date[0:50]

open_date = [d for d in open_date if d != -1]
close_date = [d for d in close_date if d != -1]

open_date=sorted(open_date)
close_date=sorted(close_date)


open_date = [datetime.strptime(y, date_format).date() for y in open_date]
close_date = [datetime.strptime(y, date_format).date() for y in close_date]

open_date, open_date_freq = countDuplicates(open_date)
close_date, close_date_freq = countDuplicates(close_date)

pprint(zip(open_date, open_date_freq))

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(date_format))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.plot(open_date, open_date_freq)

mttr = [ diffInDays(x, y) for x, y in mttr ]

mttr = map(float, mttr)
description_lengths = map(float, description_lengths)
	
m = max(mttr)
	
#mttr = [ val/m for val in mttr ]
	
m = max(description_lengths)
	
#description_lengths = [ val/(1*m) for val in description_lengths]
	
p = zip(description_lengths, hrs, mttr)
	
temp = list()
	
for x, y, z in p:
	if y:
		temp.append((x+0.00,z))
	else:
		temp.append((x,z))
	
description_lengths, mttr = zip(*temp)
	
print 'Total issues analysed: -', len(mttr)
	
#plt.plot(mttr, description_lengths, 'ro')
plt.show()	
	
	

#print calcSpearmanRho(mttr, description_lengths)
#print calcPearsonRho(mttr, description_lengths)
	
#print scipy.stats.pearsonr(mttr, description_lengths)
	
	
	
	
	
	
	
		
