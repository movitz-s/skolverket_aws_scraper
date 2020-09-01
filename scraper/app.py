import json
import boto3
import requests
import io

s3_client = boto3.client('s3')
dynamo_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    for record in event['Records']:
        schoolUnitId = record["body"]
        
        print('scraping meta for school unit', schoolUnitId)
        base_url = 'https://api.skolverket.se/planned-educations/school-units/' + schoolUnitId
        meta_resp = requests.get(base_url)
        
        dynamo_client.put_item(
            TableName='schoolMeta',
            Item={
                'schoolUnitId': {
                    'S': schoolUnitId
                },
                'document': {
                    'S': meta_resp.text
                }
            }
        )

        print('scraping stats for school', schoolUnitId)
        stats = requests.get(base_url + '/statistics').json()

        for stat in stats['_links']:
            if stat == 'self': continue

            print('scraping stat', stat, 'for school', schoolUnitId)
            stat_resp = requests.get(stats['_links'][stat]['href'])
            dynamo_client.put_item(
                TableName='schoolStats',
                Item={
                    'schoolUnitId': {
                        'S': schoolUnitId
                    },
                    'statType': {
                        'S': stat
                    },
                    'document': {
                        'S': stat_resp.text
                    }
                }
            )

        docs = requests.get(base_url + '/documents').json()[0]

        for doc in docs['documents']:
            doc_resp = requests.get(doc['url'], stream=True)
            with io.BytesIO(doc_resp.content) as file_obj:
                s3_client.upload_fileobj(file_obj, 'REDACTED', doc['fileName'])

            dynamo_client.put_item(
                TableName='schoolDocs',
                Item={
                    'schoolUnitId': {
                        'S': schoolUnitId
                    },
                    'title': {
                        'S': doc['title']
                    },
                    'meta': {
                        'S': json.dumps(doc)
                    }
                }
            )
