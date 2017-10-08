import json
from pprint import pprint
import os

import numpy as np
#import scipy.stats
#from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt


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
	
	return days//30
	
def getContribComments(json_data):
	count=0
	for obj in json_data['data']:
		if 'CONTRIBUTOR' in obj['author_association']:
			count=count+1
	
	return count
def getFirstCommentDate(json_data):
	for obj in json_data['data']:
		if 'CONTRIBUTOR' or 'OWNER'in obj['author_association']:
			return obj['created_at'][0:10]
	return None
def getCommentTimeline(json_data):
	comment_tl=str()
	for obj in json_data['data']:
		comment_tl = comment_tl+obj['created_at'][0:10]+"_"
	return comment_tl
def getDistinctParticipants(json_data):
	owner=[]
	contrib=[]
	mem=[]
	none=[]
	for obj in json_data['data']:
		if 'CONTRIBUTOR' in obj['author_association']:
			contrib.append(obj['user']['id'])
			continue
		if 'OWNER' in obj['author_association']:
			owner.append(obj['user']['id'])
			continue	
		if 'MEMBER' in obj['author_association']:
			mem.append(obj['user']['id'])
			continue	
		else:
			none.append(obj['user']['id'])
	return len(list(set(owner))),len(list(set(contrib))),len(list(set(mem))),len(list(set(none)))	

##Driver part
	
for dir_name in dir_names:
	comments_contrib = list()
	comments_timeline = list()
	print 'For ', dir_name, ' : -'
	filenames = os.listdir(os.path.join(os.getcwd(), dir_name))
	filenames = [val for val in filenames if 'comment' in val]
	for filename in filenames:
		with open(os.path.join(os.getcwd(), os.path.join(dir_name,filename))) as data_file:
			data = json.load(data_file)
		
		comments_contrib.append(getContribComments(data))	#no of comments from contributor	
		date = getFirstCommentDate(data)			#First comment date of contributor or owner
		timeline = getCommentTimeline(data)			#timeline of comments
		a,b,c,d = getDistinctParticipants(data)
		participant = str(a)+","+str(b)+","+str(c)+","+str(d)
		if timeline is not "" and date is not None:
			timeline = filename.split('_')[1].split('.')[0] + ':\n'+timeline[:-1]+"\n"+date+"\n"+participant
			comments_timeline.append(timeline)
	with open(os.path.join(os.getcwd(), os.path.join(dir_name,'cmt_timeline')),'w') as output:
		for val in comments_timeline:
			output.write(val)
			output.write('\n')
		
	print ('NO of issues '+str(len(filenames)))
	print (str(sum(comments_contrib)))
		
	
	
	
	
	
		
