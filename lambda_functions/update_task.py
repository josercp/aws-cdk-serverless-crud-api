import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])


def handler(event, context):
    try:
        # Verifying parameter
        if 'pathParameters' not in event or 'taskId' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'taskId is required in pathParameters'})
            }

        task_id = event['pathParameters']['taskId']

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

        try:
            # Trying update DynamoDB
            response = table.update_item(
                Key={
                    'taskId': task_id
                },
                UpdateExpression="set title=:t, description=:d, #s=:s",
                ExpressionAttributeNames={
                    '#s': 'status'
                },
                ExpressionAttributeValues={
                    ':t': body['title'],
                    ':d': body['description'],
                    ':s': body['status']
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            # Handling DynamoDB error
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error updating task: {e.response["Error"]["Message"]}'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }

    except Exception as e:
        # Any other error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
