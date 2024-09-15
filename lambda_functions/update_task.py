import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])


def handler(event, context):
    try:
        task_id = event['pathParameters']['taskId']
        body = json.loads(event['body'])

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
