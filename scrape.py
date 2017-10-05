import json
from pprint import pprint
import os
import numpy as np
from datetime import datetime
date_format = "%Y-%m-%d"

dir_names = [name for name in os.listdir(os.getcwd()) if os.path.isdir(name)]

#Last will be .git so we have to remove that
dir_names = dir_names[:-1]

for dir_name in dir_names:
	print 'For ', dir_name, ' : -'
	filenames = os.listdir(os.path.join(os.getcwd(), dir_name))

	countLabels = 0
	countAssignee = 0
	countReproductionSteps = 0
	lengthOfDescription = []
	timeToFix = []

	for filename in filenames:
		with open(os.path.join(os.getcwd(), os.path.join(dir_name,filename))) as data_file:
			data = json.load(data_file)

		for obj in data['data']:
			if 'pull' in obj['html_url']:
				continue

			if len(obj['labels']) > 0:
				countLabels += 1
			if len(obj['assignees']) > 0:
				countAssignee += 1
			if 'Reproduction' in obj['body']:
				countReproductionSteps += 1
			if len(obj['body']) == 0:
				continue
			a = datetime.strptime(obj['created_at'][0:10], date_format)
			if obj['state'] != 'open':
				b = datetime.strptime(obj['closed_at'][0:10], date_format)
				timeToFix.append((b-a).days)
			lengthOfDescription.append(len((obj['body'] ).split(' ') ) )

	print 'Total Issues: -' , len(lengthOfDescription)
	print 'Has labels: -', countLabels
	print 'Has Assignee: -', countAssignee
	print 'Has Reproduction Steps: -', countReproductionSteps
	print 'Mean description length: -', np.mean(lengthOfDescription)
	print 'Mean time to fix: -', np.mean(timeToFix)
