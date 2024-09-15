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

        # DynamoDB query
        try:
            response = table.get_item(
                Key={
                    'taskId': task_id
                }
            )
        except ClientError as e:
            # Handling DynamoDB error
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error retrieving task: {e.response["Error"]["Message"]}'})
            }

        # Checking if item exist
        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Task not found'})
            }

        # Success
        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }

    except Exception as e:
        # Any other error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
