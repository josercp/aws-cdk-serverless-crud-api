import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])


def handler(event, context):
    try:
        # Checking if body exist
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Body is required'})
            }

        # Trying load JSON from body
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }

        # Verifying body fields
        required_fields = ['title', 'description', 'status']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'{field} is required in the body'})
                }

        # Generate new ID
        task_id = str(uuid.uuid4())

        # Trying save item into DynamoDB
        try:
            table.put_item(
                Item={
                    'taskId': task_id,
                    'title': body['title'],
                    'description': body['description'],
                    'status': body['status']
                }
            )
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error saving task: {e.response["Error"]["Message"]}'})
            }

        # Success
        return {
            'statusCode': 201,
            'body': json.dumps({
                'taskId': task_id,
                'title': body['title'],
                'description': body['description'],
                'status': body['status']
            })
        }

    except Exception as e:
        # Any other error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
