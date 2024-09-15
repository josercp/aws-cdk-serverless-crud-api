import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])


def handler(event, context):
    try:
        task_id = event['pathParameters']['taskId']

        # Trying delete item from DynamoDB
        try:
            table.delete_item(
                Key={
                    'taskId': task_id
                }
            )
        except ClientError as e:
            # Handling DynamoDB error
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error deleting task: {e.response["Error"]["Message"]}'})
            }

        # Success
        return {
            'statusCode': 204,
            'body': ''
        }

    except Exception as e:
        # Any other error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
