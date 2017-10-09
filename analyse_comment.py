import json
from pprint import pprint
import os

import numpy as np
import scipy.stats
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


from datetime import datetime
date_format = "%Y-%m-%d"

dir_names = ['Adam']

def make_dict(dir_name):
	with open(os.path.join(os.getcwd(), os.path.join(dir_name,'cmt_timeline'))) as data_file:
		i = 1
		for line in data_file:
			if i == 1:
				issue_number = int(line[0:-2])
				i = 2
			elif i == 2:
				time_line = (line[:-1]).split('_')
				i = 3
			elif i == 3:
				i = 4
				continue
			elif i == 4:
				n_owners, n_contrib, n_members, others = map(int,((line[:-1]).split(',')))
				dic[issue_number] = list((time_line, n_owners+n_contrib+n_members+others))
				i = 1
				
				

def getDescriptionLength(json_data):
	final_data = []
	
	for obj in json_data['data']:
		if 'pull' in obj['html_url']:
			continue
		#if not any(['bug' in o['name'] for o in obj['labels']]):
		#	continue	
		if obj['body'] == None:
			final_data.append(0)
			if obj['comments'] != 0:
				l1, n = dic[str(obj['number'])]
				l1.insert(0, obj['created_at'][0:10])
				dic[obj['number']] = list((l1, 0, n))
		else:
			final_data.append(len(obj['body'].split(' ')))
			if obj['comments'] != 0:
				l1, n = dic[int(obj['number'])]
				l1.insert(0, obj['created_at'][0:10])
				dic[int(obj['number'])] = list((l1, len(obj['body'].split(' ')), n))
	
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

def calcSpearmanRho(vec1, vec2):

	rank1 = createRankVector(vec1)
	rank2 = createRankVector(vec2)
	
	sumDiffSq = sum([(d1-d2)**2 for d1, d2 in zip(rank1, rank2)])
	
	p = (6.0 * sumDiffSq)/(len(rank1)*(len(rank1)**2 - 1))
	
	p = 1 - p
	
	return p


description_lengths = list()

for dir_name in dir_names:
	print 'For ', dir_name, ' : -'
	filenames = os.listdir(os.path.join(os.getcwd(), dir_name))
	
	filenames = [val for val in filenames if 'cmt' not in val]
	
	dic = dict()
	make_dict(dir_name)
	
	#pprint(dic)

	for filename in filenames:
		with open(os.path.join(os.getcwd(), os.path.join(dir_name,filename))) as data_file:
			data = json.load(data_file)
		
		description_lengths.extend(getDescriptionLength(data))
		
	comments_TI = list()
	distinct_Users = list()
	
	for key in dic:
		temp = list()
		d = dic[key][0]
		for i in range(len(d)-1):
			temp.append(diffInDays(d[i], d[i+1]))
		comments_TI.append(np.mean(temp))
		distinct_Users.append(dic[key][2])
	
	print np.mean(comments_TI), scipy.stats.trim_mean(comments_TI, 0)
	
	
	print calcSpearmanRho(comments_TI, distinct_Users)
	
		


