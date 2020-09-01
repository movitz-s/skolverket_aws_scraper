import sys
import json
import boto3
import requests

client = boto3.client('sqs')

url = 'https://api.skolverket.se/planned-educations/school-units/?size=100'
sqs_url = sys.argv[1]

while True:
	print('Current URL:', url)
	resp = requests.get(url).json()
	if resp['_links']['last']['href'] == url: break
	url = resp['_links']['next']['href']

	for schoolUnit in resp['_embedded']['listedSchoolUnits']:
		print(schoolUnit['code'])
		response = client.send_message(
			QueueUrl=sqs_url,
			MessageBody=schoolUnit['code']
		)
